#[pyo3::pymodule]
mod _functiontrace_rs {
    use color_eyre::eyre::{OptionExt, Result, WrapErr, eyre};
    use functiontrace_server::function_trace;
    use jiff::Timestamp;
    use pyo3::prelude::*;
    use serde::{Deserialize, Serialize};
    use std::borrow::Cow;
    use std::cell::Cell;
    use std::ffi::{CStr, OsString, c_void};
    use std::io::Write;
    use std::os::unix::net::UnixStream;
    use std::sync::atomic::{AtomicBool, Ordering};
    use std::sync::{LazyLock, OnceLock};
    use std::time::Duration;

    ////////////////////////////////////////////////////////////////////////////////////////////////
    // Core Types
    ////////////////////////////////////////////////////////////////////////////////////////////////

    /// The configuration file for FunctionTrace.
    ///
    /// TODO: This is currently only used for licensing, but could reasonably be used to augment or
    /// replace some of the env vars we use.
    #[derive(Serialize, Deserialize, Clone, PartialEq)]
    struct Config {
        /// The user's license key.  This is NONCOMMERCIAL where relevant, and otherwise must
        /// contain a key that will be validated on startup.
        license_key: Option<String>,
    }

    /// The size of messagepack buffers.  This is picked somewhat arbitrarily, but should be
    /// reasonably small since we'll need one per thread, and should be large enough that we
    /// can fit many messages in before needing to do expensive UnixStream syscalls.
    const MSGPACK_BUFFER: usize = 1 << 17;

    /// Storage specific to each thread used for buffering/transmitting data.
    pub struct ThreadState {
        socket: UnixStream,

        // TODO: Conceptually this should just be a `BufWriter`, but in practice using that
        // triggers 0 byte writes that cause `functiontrace-server` to close the connection.
        // Implementing this ourselves is pretty trivial, so...
        buffer: [u8; MSGPACK_BUFFER],
        head: usize,
    }

    impl Write for ThreadState {
        /// A small [`Write`] implementation that writes to a buffer and only flushes to the socket
        /// once full.
        fn write(&mut self, src: &[u8]) -> std::io::Result<usize> {
            if !STARTED.load(Ordering::Relaxed) {
                // We haven't started yet, so we shouldn't write anything out.  This avoids logging
                // various internal setup things before we're ready.
                return Ok(src.len());
            }

            let bytes = src.len();
            let tail = self.head + bytes;

            if tail >= self.buffer.len() {
                if bytes >= self.buffer.len() {
                    // We'll never be able to fit this much.
                    return Err(std::io::Error::new(
                        std::io::ErrorKind::StorageFull,
                        "msgpack buffer too small",
                    ));
                }

                // We can't fit any more data, so need to flush.  The caller should retry after
                // this.
                self.flush()?;

                return Err(std::io::Error::new(
                    std::io::ErrorKind::Interrupted,
                    "msgpack buffer is full, flushing",
                ));
            }

            self.buffer[self.head..tail].copy_from_slice(src);
            self.head = tail;

            Ok(bytes)
        }

        /// Flush our local buffer to the socket.
        fn flush(&mut self) -> std::io::Result<()> {
            // We're about to send all the data, so reset our buffer.  Do this now to ensure we
            // don't miss it, since the buffer will be left in an invalid state if this doesn't
            // happen.
            let head = self.head;
            self.head = 0;

            self.socket.write_all(&self.buffer[..head])
        }
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////
    // Global Data
    ////////////////////////////////////////////////////////////////////////////////////////////////

    /// The UnixStream address we're using to communicate with the profile server.
    static SOCKADDR: OnceLock<OsString> = OnceLock::new();

    /// `sys.argv` for our process, which is used when registering new threads.
    static ARGV: OnceLock<String> = OnceLock::new();

    /// True iff we've started tracing and haven't been marked as terminated.  When this is
    /// set, we're allowed to send messages to the profile generation server.
    static STARTED: AtomicBool = AtomicBool::new(false);

    thread_local! {
        /// A per-thread [`ThreadState`] for writing events to.
        //
        // NOTE: The `const` block appears to be necessary in order to generate reasonable
        // assembly.  Unclear why...
        static THREAD_STATE: Cell<*mut ThreadState> = const { Cell::new(std::ptr::null_mut()) };
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////
    // Utility Functions
    ////////////////////////////////////////////////////////////////////////////////////////////////

    /// This effectively fetches the output of RDTSC, making it quick but not very useful on its
    /// own, as there is no meaningful epoch for the time.
    ///
    /// Using `Duration` is a bit weird, but for legacy reasons we're stuck with it.
    #[inline(always)]
    pub fn trace_time() -> Duration {
        let mut time = libc::timespec {
            tv_sec: 0,
            tv_nsec: 0,
        };

        unsafe {
            // SAFETY: `time` is a mutable object that's in scope for this call.
            libc::clock_gettime(libc::CLOCK_MONOTONIC, &raw mut time)
        };

        Duration::new(time.tv_sec as u64, time.tv_nsec as u32)
    }

    /// Return the [`ThreadState`] for the current thread.  This should either be None (during
    /// startup), or a valid [`ThreadState`] that has been allocated on the heap and leaked via
    /// `Box::into_raw`.
    #[inline(always)]
    pub fn thread_state() -> Option<&'static mut ThreadState> {
        let state = THREAD_STATE.get();

        if state.is_null() {
            // We shouldn't be asked to reset at thread that hasn't yet been registered.
            return None;
        }

        Some(unsafe {
            // SAFETY: state is a valid pointer to a ThreadState, since we always remove from TLS
            // before freeing.
            state.as_mut().expect("state is non-null")
        })
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////
    // Socket Communication
    ////////////////////////////////////////////////////////////////////////////////////////////////

    /// Initializes and returns the [`UnixStream`] we'll communicate to `functiontrace-server` on.
    fn message_initialize() -> UnixStream {
        let sockaddr = SOCKADDR
            .get()
            .expect("Must be initialized before setting up messaging");

        // The functiontrace-server might not be ready to receive connections yet, so we retry for
        // a bit.
        let start = std::time::Instant::now();
        loop {
            match UnixStream::connect(sockaddr) {
                Ok(s) => {
                    break s;
                }
                _ => {
                    if start.elapsed() > Duration::from_millis(1000) {
                        panic!("Timed out trying to connect to functiontrace-server");
                    }

                    std::thread::sleep(Duration::from_millis(10));
                }
            }
        }
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////
    // Tracing Implementation
    ////////////////////////////////////////////////////////////////////////////////////////////////

    /// Initialization code run on this module's import (mostly useful for adding constants)
    #[pymodule_init]
    fn init(m: &Bound<'_, PyModule>) -> PyResult<()> {
        m.add("__version__", env!("PACKAGE_VERSION"))
            .wrap_err("Failed to expose PACKAGE_VERSION")?;

        // Expose the minimum and maximum Python 3 versions we support
        m.add(
            "_min_python_version",
            env!("MIN_PYTHON_VERSION")
                .parse::<u32>()
                .wrap_err("Failed to convert MIN_PYTHON_VERSION to int")?,
        )
        .wrap_err("Failed to expose _min_python_version")?;
        m.add("_max_python_version", 13)
            .wrap_err("Failed to expose _max_python_version")?;

        color_eyre::install().wrap_err("Failed to install color_eyre")?;

        // If someone else has already installed a tracing subscriber, we'll fail to initialize
        // but get _something_ anyways.
        // This may not be possible, but I suspect a different Rust extension could interfere with
        // us so might as well be defensive.
        if let Err(e) = tracing_subscriber::fmt::fmt()
            .with_target(false)
            .with_ansi(true)
            .with_env_filter(tracing_subscriber::filter::EnvFilter::from_default_env())
            .try_init()
        {
            tracing::error!(
                error = e,
                "Failed to install tracing_subscriber for FunctionTrace"
            );
        }

        tracing::info!("Loaded `functiontrace` python module!");

        Ok(())
    }

    /// Setup the initial FunctionTrace configuration, including spawning `functiontrace-server`
    /// and sending an initialization message if necessary.
    #[pyfunction]
    #[pyo3(name = "begin_tracing")]
    #[pyo3(pass_module)]
    fn trace_initialization(
        module: &Bound<'_, PyModule>,
        output_directory: OsString,
    ) -> Result<()> {
        // The name of the env var we use to notify subprocesses that there's a trace in progress.
        const BREADCRUMB: &str = "FUNCTIONTRACE_LIVE";

        // Track whether we've been initialized yet, since that's an invalid state.
        static INITIALIZED: OnceLock<()> = OnceLock::new();

        if INITIALIZED.set(()).is_err() {
            // This can be triggered by running `functiontrace.begin_tracing()` from inside a
            // process that's already being traced.  We'll fail in this situation, but might as
            // well print a mildly helpful error message here.
            return Err(eyre!("FunctionTrace is already initialized!"));
        }

        // Store the processes' args, since threads will need it as part of the registration message.
        ARGV.set({
            // Parse args out of `sys.argv`, since it excludes the Python executable and shows the
            // script's path first.  This is much more complicated than using `std::env::args`, but
            // is more practical.
            Python::with_gil(|py| -> Result<String> {
                let argv = py
                    .import("sys")
                    .and_then(|sys| sys.getattr("argv"))
                    .wrap_err("Failed to access sys.argv")?;

                let args = argv
                    .downcast::<pyo3::types::PyList>()
                    .map_err(|e| eyre!("Failed to read sys.argv as list: {}", e))?;

                let mut full_args = args.iter().fold(String::new(), |s, arg| {
                    // Fetch the next arg as a string if possible.
                    let arg = arg
                        .downcast::<pyo3::types::PyString>()
                        .map_err(|e| eyre!("Failed to read sys.argv[x] as string: {}", e))
                        .and_then(|arg| {
                            arg.to_str()
                                .wrap_err("Failed to read Rust string out of PyString")
                        })
                        .unwrap_or("<UNKNOWN>");

                    s + " " + arg
                });

                // We'll display this in the UI, so ensure it's under (the rather
                // arbitrary) 100 chars.
                if full_args.chars().count() > 95 {
                    full_args.truncate(95);
                    full_args.push_str(" ...");
                }

                // We'll be cloning this
                full_args.shrink_to_fit();
                Ok(full_args)
            })
            .unwrap_or_else(|_err| {
                tracing::warn!("Failed to read ARGV");

                "<UNKNOWN>".into()
            })
        })
        .expect("ARGV is only set in `trace_initialization`");

        /////////////////////////////////////////////////////////////////////////
        // Server initialization
        /////////////////////////////////////////////////////////////////////////
        // Check if we're in a subprocess of a command being run under functiontrace.  If we are,
        // we should connect to the same socket.  Otherwise, we should setup the full profiling
        // configuration ourselves.
        if let Some(existing_sockaddr) = std::env::var_os(BREADCRUMB) {
            // A functiontrace-server is already running and listening.  All we need to do is save
            // the address so we know where to talk to.
            SOCKADDR
                .set(existing_sockaddr)
                .expect("sockaddr is only set in `trace_initialization`");
        } else {
            // Launch the functiontrace-server as a daemon, then record the address of the socket we'll
            // need to communicate with it on.
            let sockaddr = {
                let server = match std::process::Command::new("functiontrace-server")
                    .arg("--directory")
                    .arg(output_directory)
                    .spawn()
                {
                    Ok(server) => server,
                    Err(err) if err.kind() == std::io::ErrorKind::NotFound => {
                        eprintln!("Unable to find `functiontrace-server` in the current $PATH.");
                        eprintln!(
                            "See https://functiontrace.com#installation for installation instructions."
                        );

                        // Exit here rather than returning an error, since that'll emit a confusing
                        // Python stacktrace.
                        std::process::exit(1);
                    }
                    e => e.wrap_err("Failed to launch functiontrace-server")?,
                };

                format!("/tmp/functiontrace-server.sock.{}", server.id()).into()
            };

            Python::with_gil(|_| {
                // Register an env var so subprocesses know how to connect to our
                // profile.
                unsafe {
                    // SAFETY: `set_var` can only be done while no one else is reading or writing to the
                    // environment.  We're holding the GIL, so this _should_ be true, but there's no real
                    // way to enforce this.
                    //
                    // This doesn't seem to blow up in C even when we don't have the GIL, so
                    // it's hopefully good enough in practice since there's not really an alternative.
                    std::env::set_var(BREADCRUMB, &sockaddr);
                }
            });

            // Store the server's address so our threads know how to talk to it.
            SOCKADDR
                .set(sockaddr)
                .expect("sockaddr is only set in `trace_initialization`");

            // Send an initialization message to the server with some information about us.  This will
            // only be sent once, and all future threads/subprocesses will be associated underneath us.
            let init = {
                let python_version = Python::with_gil(|py| {
                    let version = py.version_info();

                    format!(
                        "Python {}.{}.{}",
                        version.major, version.minor, version.patch
                    )
                });

                let platform = Python::with_gil(|py| -> Result<String> {
                    let platform = py
                        .import("sys")
                        .and_then(|sys| sys.getattr("platform"))
                        .wrap_err("Failed to access sys.platform")?;

                    Ok(platform
                        .downcast::<pyo3::types::PyString>()
                        .map_err(|e| eyre!("Failed to read sys.platform as string: {}", e))?
                        .to_str()
                        .wrap_err("Failed to read Rust string out of PyString")?
                        .into())
                })
                .unwrap_or_else(|_err| {
                    tracing::warn!("Failed to read sys.platform");

                    "<UNKNOWN>".into()
                });

                function_trace::TraceInitialization {
                    program_name: ARGV
                        .get()
                        .expect("ARGV is set earlier in trace_initialization")
                        .clone(),
                    program_version: format!("py-functiontrace {}", env!("PACKAGE_VERSION")),
                    lang_version: python_version,
                    platform,
                    time: trace_time(),
                }
            };

            let mut socket = message_initialize();

            init.serialize(&mut rmp_serde::encode::Serializer::new(&mut socket))
                .wrap_err("Failed to emit TraceInitialization message")?;

            // Close the initialization socket to trigger `functiontrace-server` to
            // read our message, since otherwise it'll wait forever for more data.
            socket
                .shutdown(std::net::Shutdown::Both)
                .wrap_err("Failed to close initialization socket")?;
        }

        ////////////////////////////////////////////////////////////////////////////
        // Teardown Configuration
        ////////////////////////////////////////////////////////////////////////////
        // Ensure we're properly handling teardown scenarios, including flushing data in both
        // single and multi-threaded scenarios, and reseting anything that's needed on forks.

        // Mark that we'll need to forget some information on forks.  In
        // particular, we shouldn't think that we have a thread that's sent any
        // information.
        if unsafe { libc::pthread_atfork(None, None, Some(c_thread_reset)) } != 0 {
            return Err(eyre!("Failed to register pthread_atfork() handler"));
        }

        // Things can get into a weird state during shutdown due to GC
        // (bugs.python.org/issue21512).  Halt our tracing instead to avoid odd behaviour and
        // ensure we've flushed all our data.
        //
        // NOTE: We specifically do this rather than `Py_AtExit`  since we want to run before all
        // the Python teardown occurs.
        Python::with_gil(|py| -> Result<()> {
            py.import("atexit")
                .and_then(|atexit| atexit.getattr("register"))
                .wrap_err("Failed to access atexit.register")?
                .call1((pyo3::types::PyCFunction::new_closure(
                    py,
                    Some(c"trace_terminate"),
                    Some(c"Stop functiontrace recording"),
                    trace_terminate,
                )
                .wrap_err("Failed to convert trace_terminate to closure")?,))
                .wrap_err("Unsuccessful call")?;

            Ok(())
        })
        .wrap_err("Failed to register `atexit` handler")?;

        ////////////////////////////////////////////////////////////////////////////
        // Tracing Configuration
        ////////////////////////////////////////////////////////////////////////////
        // We now have the infrastructure setup to handle tracing.  Let's start capturing traces!

        // Register the current thread for tracing
        thread_register().wrap_err("Failed to register initial FunctionTrace thread")?;

        // Register our tracing functions with Python - both the normal one and the multithreaded
        // setup trampoline.
        unsafe {
            // SAFETY: both parameters are of the proper type.
            pyo3::ffi::PyEval_SetProfile(Some(functiontrace), std::ptr::null_mut())
        };

        Python::with_gil(|py| -> Result<()> {
            py.import("threading")
                .and_then(|threading| threading.getattr("setprofile"))
                .wrap_err("Failed to access threading.setprofile")?
                .call1((module
                    .getattr("_thread_trace_trampoline")
                    .wrap_err("Failed to retrieve trampoline")?,))
                .wrap_err("Failed to call threading.setprofile")?;

            Ok(())
        })
        .wrap_err("Failed to install multithreaded trace trampoline")?;

        // Hook various functions to enhance our logs
        crate::hooks::install().wrap_err("Failed to install Python hooks")?;

        // We're now fully setup and allowed to send messages.
        STARTED.store(true, Ordering::Relaxed);

        Ok(())
    }

    /// Called when the process is shutting down via `atexit`, notifies us to stop tracing and
    /// flush the buffer.
    ///
    /// NOTE: This is always called on the main thread.
    fn trace_terminate(
        _: &Bound<'_, pyo3::types::PyTuple>,
        _kwargs: Option<&Bound<'_, pyo3::types::PyDict>>,
    ) -> Result<()> {
        // Stop profiling and don't allow further logging, then flush any remaining messages.
        STARTED.store(false, Ordering::Relaxed);

        unsafe {
            // PyEval_SetProfile(NULL, NULL) is the proper way to deregister a profiler.
            pyo3::ffi::PyEval_SetProfile(None, std::ptr::null_mut());
        }

        // TODO: We could easily keep track of all the outstanding Writers and flush them all too.
        if let Some(writer) = thread_state() {
            thread_teardown(writer).wrap_err("Failed to teardown main thread")?;
        }

        Ok(())
    }

    /// Register a new thread, including creating the UnixStream to log messages for this thread
    /// on.
    ///
    /// A new [`ThreadState`] will be returned, which must freed once the thread has terminated.
    fn thread_register() -> Result<()> {
        if thread_state().is_some() {
            // We shouldn't have a ThreadState yet, as we're the ones that create it.
            return Err(eyre!("Thread has already been registered"));
        }

        let register =
            function_trace::FunctionTrace::RegisterThread(function_trace::ThreadRegistration {
                program_name: ARGV
                    .get()
                    .ok_or_eyre(eyre!("sys.argv hasn't been parsed yet"))?
                    .clone(),
                pid: std::process::id() as usize,
                time: trace_time(),
            });

        let mut socket = message_initialize();

        // Write this registration message directly to the socket to ensure we'll record
        // *something* for this thread even in the case where we quickly exit.
        //
        // TODO: We should have a different approach that doesn't require explicit flushing.
        // https://crates.io/crates/iceoryx2 looks like a good option once we're fully in Rust.
        register
            .serialize(&mut rmp_serde::encode::Serializer::new(&mut socket))
            .wrap_err("Failed to emit RegisterThread message")?;

        // Initialize the `ThreadState` for this thread, then associate the socket with it.
        //
        // We'll move this state into thread local storage, and will need to recover it on
        // termination in order to free it.
        let state = Box::into_raw(Box::new(ThreadState {
            socket,

            buffer: [0u8; MSGPACK_BUFFER],
            head: 0,
        }));

        // Store our state in thread-specific storage so we can find it in the future.
        // Tracing begins for the thread at this point, since we've now published `state` for other
        // functions to start using.
        THREAD_STATE.set(state);

        Ok(())
    }

    #[unsafe(no_mangle)]
    extern "C" fn c_thread_teardown(state: *mut c_void) {
        if state.is_null() {
            // We never fully initialized this thread, so skip teardown.
            return;
        }

        let writer = unsafe {
            // SAFETY: writer is a valid pointer to an initialized `ThreadState`.
            &mut (state as *mut ThreadState)
                .as_mut()
                .expect("state is non-null")
        };

        thread_teardown(writer).expect("Failed to tear down FunctionTrace thread")
    }

    /// Tear down the given thread by flushing any outstanding messages.
    ///
    /// This is called when the thread has shut down, including in multithread/process situations.
    pub fn thread_teardown(writer: &mut ThreadState) -> Result<()> {
        writer
            .flush()
            .wrap_err("Failed to flush remaining messages")?;

        // TODO: We should tear down the socket to avoid leaking O(# threads) resources.
        // Historically doing this has crashed for some reason...
        //
        // TODO: And we should probably free state since it's pretty large...
        Ok(())
    }

    #[unsafe(no_mangle)]
    extern "C" fn c_thread_reset() {
        thread_reset().expect("Failed to reset FunctionTrace thread state")
    }

    /// We have some existing thread state that we should free and forget about before resuming
    /// logging.
    ///
    /// This is useful when we've just forked and want to ensure we don't reuse an existing socket.
    fn thread_reset() -> Result<()> {
        if !STARTED.load(Ordering::Relaxed) {
            // We haven't actually started yet, but are for some reason being asked
            // to fork.  This appears to be OS dependent.
            return Ok(());
        }

        // Load the old state so we can free it.
        let state = thread_state().ok_or_eyre(eyre!("Thread wasn't yet registered"))?;

        // Remove the TLS reference so no one else can load state after we've freed it.
        THREAD_STATE.set(std::ptr::null_mut());

        // Free the thread's state, including the socket
        unsafe {
            // SAFETY: `state` came from `Box::into_raw` previously and can only be freed once.
            let _ = Box::from_raw(state);
        }

        // Create a new thread for this process.  We don't need to start an entire new trace like
        // with subprocess calls since we were forked and therefore already share our
        // configuration.
        thread_register().wrap_err("Failed to register new thread")?;

        Ok(())
    }

    /// Internal helper that installs FunctionTrace on each new thread's startup.
    ///
    /// This is installed as the setprofile() handler for new threads by threading.setprofile().
    /// On its first execution, it initializes tracing for the thread, including creating the
    /// thread state, before replacing itself with the normal Fprofile_FunctionTrace handler.
    #[pyfunction]
    #[pyo3(name = "_thread_trace_trampoline")]
    fn thread_trace_trampoline(_frame: PyObject, _event: PyObject, _arg: PyObject) -> Result<()> {
        // Register the current thread for tracing
        thread_register().wrap_err("Failed to register new FunctionTrace thread")?;

        // Replace our setprofile() handler with the real one.
        unsafe {
            // SAFETY: both parameters are of the proper type.
            pyo3::ffi::PyEval_SetProfile(Some(functiontrace), std::ptr::null_mut())
        };

        // We previously called into `Fprofile_FunctionTrace` here to manually record this call,
        // but that's both not very interesting as well as causes crashes on startup for some
        // Python versions (due to insufficiently initialized frames), so we don't do that anymore.
        Ok(())
    }

    /// Enable memory tracing for the current program.  This is implemented by attaching wrapper
    /// versions of malloc/free/etc to all the current allocators.
    ///
    /// NOTE: Memory tracing may have up to 40% overhead on traces with many small allocations, so
    /// is not enabled by default.
    #[pyfunction]
    #[pyo3(name = "enable_tracememory")]
    fn allocations_record() -> Result<()> {
        // True iff we've enabled memory allocations.
        static ENABLE_MEM_TRACING: AtomicBool = AtomicBool::new(false);

        // Mark that memory tracing is enabled if it wasn't already.
        if ENABLE_MEM_TRACING.swap(true, Ordering::Relaxed) {
            // We've already enabled memory tracing, so there's nothing left to do.
            return Ok(());
        }

        // We'll immediately begin recording allocations, even if we haven't started yet, since
        // any logs before `STARTED = true` will be dropped.

        // Hook each of the possible allocators
        for domain in [
            pyo3::ffi::PyMemAllocatorDomain::PYMEM_DOMAIN_RAW,
            pyo3::ffi::PyMemAllocatorDomain::PYMEM_DOMAIN_MEM,
            pyo3::ffi::PyMemAllocatorDomain::PYMEM_DOMAIN_OBJ,
        ] {
            use crate::allocation_wrappers;

            // Fetch the original allocator and leak it, since we'll need to refer back to it.
            let original = Box::into_raw(Box::new(pyo3::ffi::PyMemAllocatorEx {
                ctx: std::ptr::null_mut(),
                malloc: None,
                calloc: None,
                realloc: None,
                free: None,
            }));

            unsafe {
                // SAFETY: `original` is a valid object with a 'static lifetime
                pyo3::ffi::PyMem_GetAllocator(domain, original)
            };

            // Wrap the original allocator in our wrappers which log and then call back into it.
            let mut wrapper = pyo3::ffi::PyMemAllocatorEx {
                ctx: original as *mut _,
                malloc: Some(allocation_wrappers::log_malloc),
                calloc: Some(allocation_wrappers::log_calloc),
                realloc: Some(allocation_wrappers::log_realloc),
                free: Some(allocation_wrappers::log_free),
            };

            unsafe {
                // SAFETY: `wrapper` is a valid object for the lifetime of this call
                pyo3::ffi::PyMem_SetAllocator(domain, &raw mut wrapper)
            };
        }

        Ok(())
    }

    /// The core logging function for FunctionTrace.  Configured by `PyEval_SetProfile`, and used
    /// to record all function calls/returns.
    extern "C" fn functiontrace(
        _obj: *mut pyo3::ffi::PyObject,
        frame: *mut pyo3::ffi::PyFrameObject,
        what: i32,
        arg: *mut pyo3::ffi::PyObject,
    ) -> i32 {
        let Some(mut writer) = thread_state() else {
            // No reason to look at the event since we can't log it yet.
            return 0;
        };

        if !STARTED.load(Ordering::Relaxed) {
            // We aren't running (either starting up or shutting down), so shouldn't write
            // anything.
            return 0;
        }

        let time = trace_time();

        // Return the function name when we're in a C_* context.
        let c_func_name = || {
            let func = arg as *mut pyo3::ffi::PyCFunctionObject;

            unsafe {
                // SAFETY: In the `C_*` cases, `arg` is a non-NULL `*PyCFunctionObject`, which
                // always contains a valid method.
                let method = (*func).m_ml;
                (*method).ml_name
            }
        };
        // Given a C string sourced from Python, convert it to a Cow that can be serialized.
        let cstr_to_cow = |ptr: *const i8| {
            if !ptr.is_null() {
                unsafe {
                    // SAFETY: `ptr` is non-NULL and contains a valid C string.
                    // TODO: Can this change underneath us?
                    CStr::from_ptr(ptr)
                }
                .to_str()
                .unwrap_or("<invalid string>")
                .into()
            } else {
                Cow::Borrowed("<null>")
            }
        };
        match what {
            pyo3::ffi::PyTrace_CALL | pyo3::ffi::PyTrace_RETURN => {
                // Cache information about each frame we see so that we don't need to look it up
                // every time, which involves expensive Python operations.
                static FRAMES: LazyLock<
                    dashmap::DashMap<usize, (Cow<'static, str>, Cow<'static, str>)>,
                > = LazyLock::new(|| {
                    dashmap::DashMap::with_capacity(
                        // Even small programs will have a decent amount of function calls in the
                        // interpreter setup.
                        512,
                    )
                });

                let entry = FRAMES.entry(frame.addr()).or_insert_with(|| {
                    // We've never seen this frame before, so we'll need to load its
                    // information.  This is fairly slow, since it'll involve going via Python
                    // rather than fast struct accesses.
                    let code = unsafe {
                        // SAFETY: frame is guaranteed to be a valid PyFrameObject

                        // We'll be storing `frame` in our hashmap, so we don't want anyone
                        // else freeing it.
                        pyo3::ffi::Py_IncRef(frame as *mut pyo3::ffi::PyObject);

                        pyo3::ffi::PyFrame_GetCode(frame) as *mut pyo3::ffi::PyObject
                    };

                    Python::with_gil(|py| {
                        let code = unsafe {
                            // SAFETY: code is guaranteed to be a valid PyCodeObject since it
                            // came from `PyFrame_GetCode`.
                            Bound::from_borrowed_ptr(py, code)
                        };

                        // Given a Python object that _should_ be a string, convert it into an
                        // a Rust string.
                        let unicode_converter = |pyobj: PyResult<Bound<'_, PyAny>>| {
                            pyobj
                                .map(|obj| {
                                    if let Ok(filename) = obj.downcast::<pyo3::types::PyString>() {
                                        Cow::from(filename.to_string_lossy().into_owned())
                                    } else {
                                        Cow::Borrowed("<UNKNOWN>")
                                    }
                                })
                                .unwrap_or_else(|_| Cow::Borrowed("<NONE>"))
                        };

                        let filename =
                            unicode_converter(code.getattr(pyo3::intern!(py, "co_filename")));
                        let func_name = unicode_converter(code.getattr(if cfg!(Py_3_11) {
                            // co_qualname is better but was only added in 3.11.
                            pyo3::intern!(py, "co_qualname")
                        } else {
                            pyo3::intern!(py, "co_name")
                        }));

                        (filename, func_name)
                    })
                });

                if what == pyo3::ffi::PyTrace_CALL {
                    let linenumber = unsafe { pyo3::ffi::PyFrame_GetLineNumber(frame) }
                        .try_into()
                        .expect("Invalid line number for executing frame");

                    function_trace::FunctionTrace::Call {
                        filename: entry.0.clone(),
                        func_name: entry.1.clone(),
                        linenumber,
                        time,
                    }
                    .serialize(&mut rmp_serde::encode::Serializer::new(&mut writer))
                    .expect("Failed to emit Call message");
                } else {
                    function_trace::FunctionTrace::Return {
                        func_name: entry.1.clone(),
                        time,
                    }
                    .serialize(&mut rmp_serde::encode::Serializer::new(&mut writer))
                    .expect("Failed to emit Return message")
                }
            }
            pyo3::ffi::PyTrace_C_CALL => {
                let func = unsafe {
                    // SAFETY: In the `C_CALL` case, `arg` is guaranteed to be a non-NULL pointer
                    // to a `PyCFunctionObject`.
                    &*(arg as *mut pyo3::ffi::PyCFunctionObject)
                };

                let func_name = cstr_to_cow(c_func_name());

                // We either belong to a module or are a method on a class.
                if !func.m_module.is_null() {
                    // NOTE: _Typically_ `m_module` is a PyModule, but there are no requirements on
                    // what type it needs to be!  In practice, we only see PyModules and PyStrings.
                    Python::with_gil(|py| {
                        let m_module = unsafe {
                            // SAFETY: m_module is a non-NULL pointer to a valid Python object.
                            Bound::from_borrowed_ptr(py, func.m_module)
                        };

                        if let Ok(module) = m_module.downcast::<pyo3::types::PyModule>() {
                            // This is a PyModule, so get its name if possible.
                            let name = module.name();
                            let module_name = if let Ok(name) = &name {
                                name.to_cow().unwrap_or(Cow::Borrowed("<invalid string>"))
                            } else {
                                Cow::Borrowed("<unnamed module>")
                            };

                            function_trace::FunctionTrace::NativeCall {
                                module_name,
                                func_name,
                                time,
                            }
                            .serialize(&mut rmp_serde::encode::Serializer::new(&mut writer))
                        } else {
                            let module_name =
                                if let Ok(module) = m_module.downcast::<pyo3::types::PyString>() {
                                    module.to_cow().unwrap_or(Cow::Borrowed("<invalid string>"))
                                } else {
                                    if let Ok(typ) = m_module.get_type().qualname().map(|x| x.to_string()) {
                                        tracing::warn!(type = typ, "Failed to read module name due to unexpected type");
                                    } else {
                                        tracing::warn!("Failed to read module name due to indecipherable type");
                                    }

                                    Cow::Borrowed("<unknown module>")
                                };
                            function_trace::FunctionTrace::NativeCall {
                                module_name,
                                func_name,
                                time,
                            }
                            .serialize(&mut rmp_serde::encode::Serializer::new(&mut writer))
                        }
                    })
                } else {
                    // We don't belong to a module, so must be a class method.
                    let module_name = if !func.m_self.is_null() {
                        cstr_to_cow(unsafe {
                            // SAFETY: Since `m_self` is non-NULL, it must point to a valid
                            // PyObject, which is required to have a live and fully initialized
                            // `ob_type` member.
                            (*(*func.m_self).ob_type).tp_name
                        })
                    } else {
                        Cow::Borrowed("<unknown module>")
                    };

                    function_trace::FunctionTrace::NativeCall {
                        module_name,
                        func_name,
                        time,
                    }
                    .serialize(&mut rmp_serde::encode::Serializer::new(&mut writer))
                }
                .expect("Failed to emit NativeCall message");
            }
            pyo3::ffi::PyTrace_C_RETURN | pyo3::ffi::PyTrace_C_EXCEPTION => {
                if what == pyo3::ffi::PyTrace_C_EXCEPTION {
                    // C exceptions aren't exposed in a particularly interesting fashion, since they're
                    // done using the `PyErr_*` functions plus a NULL return value.
                    // However, if a `C_EXCEPTION` event is sent, we won't receive the corresponding
                    // `C_RETURN` event, so in practice we treat both of these events the same.
                    //
                    // TODO: Should we try exposing information about them?  We'd probably need to
                    // change the `Exception` format in `functiontrace-server`.
                }

                function_trace::FunctionTrace::NativeReturn {
                    func_name: cstr_to_cow(c_func_name()),
                    time,
                }
                .serialize(&mut rmp_serde::encode::Serializer::new(&mut writer))
                .expect("Failed to emit NativeReturn message");
            }
            pyo3::ffi::PyTrace_EXCEPTION => {
                // TODO: Actually handle exceptions and do something interesting.
                // We unfortunately can't get these from `PyEval_SetProfile`, so we'd need to use a
                // different method to capture them.
            }
            v => {
                tracing::error!(event = v, "Unexpected PyTrace message!");
            }
        };

        0
    }

    ////////////////////////////////////////////////////////////////////////////
    // Commercial support
    ////////////////////////////////////////////////////////////////////////////

    /// Load our configuration, including:
    /// - Displaying a first-use message
    /// - Creating the configuration file if non-existent
    /// - Validating license keys
    ///
    /// We default to being permissive, and want to make this as non-invasive as possible for
    /// non-commercial users.
    #[pyfunction]
    fn load_config() -> Result<()> {
        use owo_colors::OwoColorize;

        ////////////////////////////////////////////////////////////////////////
        // Load or initialize config file
        ////////////////////////////////////////////////////////////////////////
        // Load configuration from the standard directory, or `~/.config` if the XDG spec isn't
        // being followed.
        let config_path = {
            if let Some(config_path) = std::env::var_os("FUNCTIONTRACE_CONFIGFILE") {
                // Allow `FUNCTIONTRACE_CONFIGFILE` as an override (mostly for tests, but it could
                // be useful for Nix users or others).
                std::path::PathBuf::from(config_path)
            } else if let Some(mut config_dir) = std::env::var_os("XDG_CONFIG_HOME")
                .map(std::path::PathBuf::from)
                .or_else(|| {
                    std::env::home_dir().map(|mut home| {
                        home.push(".config");
                        home
                    })
                })
            {
                config_dir.push("functiontrace.toml");
                config_dir
            } else {
                // If we fail to find a reasonable config path, we'll just pretend everything is
                // fine.
                tracing::error!(
                    "Failed to find FunctionTrace config directory - proceeding without loading config"
                );
                return Ok(());
            }
        };

        let config = if let Ok(config) = std::fs::read(&config_path)
            .wrap_err("Failed to read config file")
            .and_then(|x| toml::from_slice::<Config>(&x).wrap_err("Failed to parse config file"))
        {
            // We successfully loaded an existing config file.
            config
        } else {
            // There's no config file, so assume this is the first time FunctionTrace has been
            // used and generate a new one.
            let logo = "\
███████╗██╗   ██╗███╗   ██╗ ██████╗████████╗██╗ ██████╗ ███╗   ██╗████████╗██████╗  █████╗  ██████╗███████╗\n\
██╔════╝██║   ██║████╗  ██║██╔════╝╚══██╔══╝██║██╔═══██╗████╗  ██║╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██╔════╝\n\
█████╗  ██║   ██║██╔██╗ ██║██║        ██║   ██║██║   ██║██╔██╗ ██║   ██║   ██████╔╝███████║██║     █████╗  \n\
██╔══╝  ██║   ██║██║╚██╗██║██║        ██║   ██║██║   ██║██║╚██╗██║   ██║   ██╔══██╗██╔══██║██║     ██╔══╝  \n\
██║     ╚██████╔╝██║ ╚████║╚██████╗   ██║   ██║╚██████╔╝██║ ╚████║   ██║   ██║  ██║██║  ██║╚██████╗███████╗\n\
╚═╝      ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚══════╝\n";

            // Render the logo like a flamechart using Python-esque colors.
            for (row, line) in logo.lines().enumerate() {
                for (x, c) in line.chars().enumerate() {
                    // heights[x] represents the height of the flamechart at position x
                    //
                    // NOTE: These values were somewhat arbitrarily chosen, but the bottom row is
                    // always covered.
                    let heights = [
                        1, 1, 3, 3, 4, 4, 4, 4, 3, 2, 2, 2, 2, 2, 3, 4, 5, 5, 3, 3, 1, 2, 2, 3, 4,
                        4, 4, 4, 4, 4, 4, 3, 3, 3, 5, 5, 6, 6, 6, 5, 5, 3, 2, 2, 2, 3, 5, 5, 5, 5,
                        5, 2, 2, 4, 6, 6, 6, 3, 2, 3, 3, 5, 3, 3, 5, 5, 5, 5, 3, 3, 2, 2, 1, 1, 1,
                        1, 1, 2, 2, 2, 4, 4, 4, 3, 4, 3, 3, 3, 3, 2, 2, 5, 5, 5, 5, 5, 5, 4, 3, 2,
                        2, 2, 2, 3, 4, 5, 5, 0,
                    ];

                    // We look at chart depth from top to bottom.
                    let current_depth = 6 - row;

                    if current_depth > heights[x] {
                        print!("{}", c.blue());
                    } else {
                        print!("{}", c.fg::<owo_colors::colors::xterm::FlushOrange>());
                    }
                }
                println!();
            }
            println!();
            println!(
                "{}",
                "Welcome to FunctionTrace, a low overheard tracing profiler for Python".bold()
            );
            println!();
            println!(
                "Please see {} for instructions on setup and use.",
                "https://functiontrace.com".underline().cyan()
            );
            println!(
                "FunctionTrace will emit profile files ({}) that must be loaded by the",
                "functiontrace.*.tar.gz".dimmed()
            );
            println!(
                "Firefox Profiler ({}) for analysis.",
                "https://profiler.firefox.com/".underline().cyan()
            );
            println!();

            let config = Config { license_key: None };

            match std::fs::write(
                &config_path,
                toml::to_string_pretty(&config).wrap_err("Failed to serialize config file")?,
            ) {
                Ok(_) => {
                    println!(
                        "{}{}",
                        format_args!("Default config saved to {}", config_path.display().bold())
                            .dimmed(),
                        ".  This startup message will not be shown again.".dimmed()
                    );
                    println!();
                }
                Err(e) => {
                    eprintln!(
                        "Failed to create default FunctionTrace config file at {}: {e}",
                        config_path.display().dimmed(),
                    );
                }
            };

            config
        };

        // We need to write out the config if it's changed.  Track the new and old configs so we
        // can tell.
        let mut new_config = config.clone();

        ////////////////////////////////////////////////////////////////////////
        // Find their license key
        ////////////////////////////////////////////////////////////////////////
        // Demo keys have the same general shape as a UUID, but include the expiration time
        const DEMO_KEY_PREFIX: &str = "TRIALKEYX-";
        const DEMO_KEY_FORMAT: &str = "%Y-%m%d-%H%M-%S%z";
        const DEMO_KEY_SUFFIX: &str = "TRIAL";

        let license_key = if let Some(license_key) = &config.license_key {
            license_key.clone()
        } else {
            println!("FunctionTrace is open-source and may freely be used noncommercially under");
            println!(
                "the Prosperity Public License 3.0 ({}).",
                "https://prosperitylicense.com/".underline().cyan()
            );
            println!();

            /// Print a prompt, then read lines of input repeatedly until it successfully parses.
            fn read_input<T, F>(prompt: std::fmt::Arguments, parser: F) -> Result<T>
            where
                F: Fn(&String) -> Option<T>,
            {
                let mut input = String::new();

                loop {
                    print!("{}", prompt);
                    std::io::stdout().flush()?;

                    input.clear();
                    std::io::stdin().read_line(&mut input)?;

                    if let Some(result) = parser(&input) {
                        return Ok(result);
                    }
                    Python::with_gil(|py| {
                        // We need to check with the Python interpreter during loops, otherwise we
                        // might not receive ctrl-c events.
                        py.check_signals()
                    })?;
                }
            }

            let commercial = read_input(
                format_args!(
                    "{} {}: ",
                    "Are you using FunctionTrace commercially?".bold(),
                    "[yes/no]".dimmed()
                ),
                |input| match input.chars().next() {
                    Some('y') => Some(true),
                    Some('n') => Some(false),
                    _ => {
                        eprintln!(
                            "Failed to read {} or {} input.",
                            "yes".dimmed(),
                            "no".dimmed()
                        );
                        None
                    }
                },
            )?;

            let key = if !commercial {
                "NONCOMMERCIAL".to_string()
            } else {
                println!();
                println!(
                    "The Prosperity Public License allows for a single 30 day trial period for commercial users."
                );
                let demo = read_input(
                    format_args!(
                        "{} {}: ",
                        "Is this your company's first time using FunctionTrace?".bold(),
                        "[yes/no]".dimmed()
                    ),
                    |input| match input.chars().next() {
                        Some('y') => Some(true),
                        Some('n') => Some(false),
                        _ => {
                            eprintln!(
                                "Failed to read {} or {} input.",
                                "yes".dimmed(),
                                "no".dimmed()
                            );
                            None
                        }
                    },
                )?;

                if demo {
                    // They haven't used FunctionTrace yet, so we'll generate them a demo key
                    // that's valid for 30 days.
                    let expiration = Timestamp::now()
                        .checked_add(Duration::from_secs(3600 * 24 * 30))
                        .expect("30 days in the future is valid");

                    // Generate a key formatted like a UUID, but with the expiration time included
                    format!(
                        "{DEMO_KEY_PREFIX}{}{DEMO_KEY_SUFFIX}",
                        expiration.strftime(DEMO_KEY_FORMAT)
                    )
                } else {
                    println!();
                    println!(
                        "Commercial users must purchase an alternative license via {}.",
                        "https://functiontrace.com".underline().cyan()
                    );

                    read_input(
                        format_args!("{}: ", "Enter your FunctionTrace license key".bold()),
                        |input| {
                            if input.trim().chars().filter(|&c| c == '-').count() == 4 {
                                // The key looks plausible.  We'll validate it later.
                                Some(input.trim().to_string())
                            } else {
                                eprintln!(
                                    "Invalid license format.  FunctionTrace license keys look like {}.",
                                    "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX".dimmed()
                                );
                                None
                            }
                        },
                    )?
                }
            };

            new_config.license_key = Some(key.clone());
            key
        };

        ////////////////////////////////////////////////////////////////////////
        // Validate the license key
        ////////////////////////////////////////////////////////////////////////
        let valid_license = if license_key == "NONCOMMERCIAL" {
            // The user has asserted that they're not using FunctionTrace for commercial
            // purposes.  Nothing left to validate here.
            true
        } else if let Some(demo_key) = license_key
            .strip_prefix(DEMO_KEY_PREFIX)
            .and_then(|s| s.strip_suffix(DEMO_KEY_SUFFIX))
        {
            // The user has a demo key that's valid for 30 days from creation.
            let now = Timestamp::now();

            if let Ok(valid_expiration) = Timestamp::strptime(DEMO_KEY_FORMAT, demo_key) {
                if now
                    .until(valid_expiration)
                    .map_or(false, |remaining| remaining.is_positive())
                {
                    // The license is still valid
                    eprintln!(
                        "{}: You're using a trial license that expires on {}.  Please visit {} to acquire a full license.",
                        "FunctionTrace trial".yellow().bold(),
                        valid_expiration.strftime("%Y-%m-%d").dimmed(),
                        "https://functiontrace.com".underline().cyan(),
                    );
                    true
                } else {
                    eprintln!(
                        "{}: You're using a trial license that expired on {}.  Please visit {} to acquire a full license.",
                        "FunctionTrace trial expired".red().bold(),
                        valid_expiration.strftime("%Y-%m-%d").dimmed(),
                        "https://functiontrace.com".underline().cyan(),
                    );
                    false
                }
            } else {
                // This demo key doesn't parse, so it's presumably invalid.
                eprintln!(
                    "{}: your company's trial has expired.  Please visit {} to acquire a license.",
                    "FunctionTrace trial expired".red().bold().dimmed(),
                    "https://functiontrace.com".underline().cyan(),
                );
                false
            }
        } else {
            // The user has a commercial license key.  Validate it against our server
            let client = reqwest::blocking::Client::new();
            if let Ok(license_check) = client
                .get("https://license.functiontrace.com")
                .header("functiontrace-key", &license_key)
                .timeout(
                    // We set a short timeout, since the license server should respond within a few
                    // ms and we don't want to block users if it can't be contacted.
                    Duration::from_secs(2),
                )
                .send()
            {
                /// Represents useful information about a given license
                #[derive(Deserialize)]
                struct LicenseInfo {
                    #[serde(rename = "Seats")]
                    seats: u32,
                    #[serde(rename = "Expires")]
                    expires: Timestamp,
                }

                match license_check.status() {
                    reqwest::StatusCode::OK => {
                        // This key is live!
                        if let Ok(info) = license_check.json::<LicenseInfo>() {
                            tracing::info!(
                                seats = info.seats,
                                expiration = info.expires.strftime("%F").to_string(),
                                "Valid license loaded"
                            );
                        } else {
                            tracing::info!(
                                seats = "unknown",
                                expiration = "unknown",
                                "Valid license loaded"
                            );
                        }
                    }
                    reqwest::StatusCode::BAD_REQUEST => {
                        // This license does not and has never existed.
                        eprintln!(
                            "{}: {} is not a valid FunctionTrace license.",
                            "Invalid Functiontrace license".red().bold(),
                            license_key.dimmed()
                        );

                        // Mark this license key for deletion.  We don't need to inform the user,
                        // since it never could have worked.
                        new_config.license_key = None;
                    }
                    reqwest::StatusCode::PAYMENT_REQUIRED => {
                        // This license used to be valid but isn't anymore.
                        if let Ok(info) = license_check.json::<LicenseInfo>() {
                            eprintln!(
                                "{}: {} expired on {}.  Please visit {} to acquire a new license.",
                                "FunctionTrace license expired".red().bold(),
                                license_key.dimmed(),
                                info.expires.strftime("%F").bold(),
                                "https://functiontrace.com".underline().cyan(),
                            );
                        } else {
                            eprintln!(
                                "{}: {} has expired.  Please visit {} to acquire a new license.",
                                "FunctionTrace license expired".red().bold(),
                                license_key.dimmed(),
                                "https://functiontrace.com".underline().cyan(),
                            );
                        }

                        eprintln!(
                            "Removing expired FunctionTrace license key from {}.",
                            config_path.display().dimmed()
                        );
                        new_config.license_key = None;
                    }
                    reqwest::StatusCode::INTERNAL_SERVER_ERROR => {
                        // The license server crashed?
                        tracing::warn!(
                            "License server returned an error - assuming license is valid"
                        );
                    }
                    status => {
                        tracing::warn!(
                            code = status.as_u16(),
                            "License server returned an unexpected code - assuming license is valid"
                        );
                    }
                };

                // If there's still a license key stored in the config file, we must've validated
                // it.
                new_config.license_key.is_some()
            } else {
                // We didn't successfully talk to the license server.  Assume everything is fine.
                true
            }
        };

        ////////////////////////////////////////////////////////////////////////
        // Save the updated config
        ////////////////////////////////////////////////////////////////////////
        if new_config != config {
            // We updated the configuration file, so save it out.
            if let Err(e) = std::fs::write(
                &config_path,
                toml::to_string_pretty(&new_config).wrap_err("Failed to serialize config file")?,
            ) {
                eprintln!(
                    "Failed to update FunctionTrace config file at {}: {e}",
                    config_path.display().dimmed(),
                );
            };
        }

        if !valid_license {
            // We've already printed information about what's happening, so it's safe to just kill
            // the process.
            std::process::exit(1);
        }

        Ok(())
    }
}

/// Allocation hooks and helpers for tracing Python memory allocator operations.
mod allocation_wrappers {
    use functiontrace_server::function_trace;
    use serde::Serialize;
    use std::ffi::c_void;

    /// Log the given allocation details.
    fn allocation_log<F: FnOnce() -> function_trace::AllocationDetails>(msg: F) {
        if let Some(mut writer) = crate::_functiontrace_rs::thread_state() {
            function_trace::FunctionTrace::Allocation {
                time: crate::_functiontrace_rs::trace_time(),
                details: msg(),
            }
            .serialize(&mut rmp_serde::encode::Serializer::new(&mut writer))
            .expect("Failed to emit Allocation message");
        }
    }

    /// Given an allocator->ctx for a logging allocator, convert it to point to the original
    /// (wrapped) allocator.
    #[inline(always)]
    fn allocator_ctx(ctx: *mut c_void) -> pyo3::ffi::PyMemAllocatorEx {
        unsafe {
            // SAFETY: ctx is non-NULL and points to a `PyMemAllocatorEx` (checked in
            // `allocations_record`).
            *(ctx as *mut pyo3::ffi::PyMemAllocatorEx)
        }
    }

    #[unsafe(no_mangle)]
    pub extern "C" fn log_malloc(ctx: *mut c_void, bytes: usize) -> *mut c_void {
        let wrapped_allocator = allocator_ctx(ctx);
        let addr = wrapped_allocator
            .malloc
            .map(|malloc| malloc(wrapped_allocator.ctx, bytes))
            .unwrap_or(std::ptr::null_mut());

        allocation_log(|| function_trace::AllocationDetails::Alloc {
            bytes,
            addr: addr as usize,
        });

        addr
    }

    #[unsafe(no_mangle)]
    pub extern "C" fn log_calloc(ctx: *mut c_void, nelems: usize, elsize: usize) -> *mut c_void {
        let wrapped_allocator = allocator_ctx(ctx);
        let addr = wrapped_allocator
            .calloc
            .map(|calloc| calloc(wrapped_allocator.ctx, nelems, elsize))
            .unwrap_or(std::ptr::null_mut());

        allocation_log(|| function_trace::AllocationDetails::Alloc {
            bytes: nelems * elsize,
            addr: addr as usize,
        });

        addr
    }

    #[unsafe(no_mangle)]
    pub extern "C" fn log_realloc(
        ctx: *mut c_void,
        old_addr: *mut c_void,
        new_size: usize,
    ) -> *mut c_void {
        let wrapped_allocator = allocator_ctx(ctx);
        let addr = wrapped_allocator
            .realloc
            .map(|realloc| realloc(wrapped_allocator.ctx, old_addr, new_size))
            .unwrap_or(std::ptr::null_mut());

        allocation_log(|| function_trace::AllocationDetails::Realloc {
            bytes: new_size,
            old_addr: old_addr as usize,
            new_addr: addr as usize,
        });

        addr
    }

    #[unsafe(no_mangle)]
    pub extern "C" fn log_free(ctx: *mut c_void, old_addr: *mut c_void) {
        if old_addr.is_null() {
            // Abort quickly, since `free(NULL)` is surprisingly common and is defined to be a
            // NOOP.
            return;
        }

        let wrapped_allocator = allocator_ctx(ctx);
        if let Some(free) = wrapped_allocator.free {
            free(wrapped_allocator.ctx, old_addr)
        }

        allocation_log(|| function_trace::AllocationDetails::Free {
            old_addr: old_addr as usize,
        });
    }
}

/// Allocation hooks and helpers for tracing Python memory allocator operations.
mod hooks {
    use crate::_functiontrace_rs::trace_time;
    use color_eyre::eyre::{Result, WrapErr};
    use functiontrace_server::function_trace;
    use pyo3::ffi::PyObject;
    use pyo3::prelude::*;
    use serde::Serialize;
    use std::borrow::Cow;
    use std::sync::OnceLock;

    /// Install all the hooks by generating function capable of overriding an existing Python
    /// function, then attaching enough information about the original function to call it.
    pub fn install() -> Result<()> {
        for hook in HOOKS.iter() {
            Python::with_gil(|py| -> Result<()> {
                let (module_name, method_name) = hook
                    .target
                    .rsplit_once(".")
                    .expect("Each hook is a <module>.<method>");

                // Fetch the target module.method
                let module = py.import(module_name).wrap_err("Failed to import module")?;
                let orig = module
                    .getattr(method_name)
                    .wrap_err("Failed to retrieve module")?
                    .unbind();

                // Save the original method, since we'll need to call it from our wrapper function.
                hook.original
                    .set(orig)
                    .expect("We're the only function that sets the hooks");

                // Create a new Python function and overwrite the old one with it
                let func = pyo3::types::PyCFunction::new_with_keywords(
                    py,
                    hook.wrapper,
                    Box::leak(
                        // The function name must live for as long as it's reachable by Python
                        // (forever).
                        std::ffi::CString::new(method_name)
                            .wrap_err("Failed to convert module name to C-string")?
                            .into_boxed_c_str(),
                    ),
                    c"FunctionTrace internal wrapper for print",
                    Some(&module),
                )
                .wrap_err("Failed to generate PyCFunction")?;
                module
                    .add(method_name, func)
                    .wrap_err("Failed to override method")
            })
            .wrap_err_with(|| format!("Failed to hook {}", hook.target))?;
        }

        Ok(())
    }

    ////////////////////////////////////////////////////////////////////////////
    // Hooking Framework
    ////////////////////////////////////////////////////////////////////////////

    /// Implementation details behind [`hooks`].
    ///
    /// Keep a:
    /// - counter that is incremented for each hook tuple we're passed, allowing us to know the
    ///   index of that hook
    /// - accumulator that gathers the counted hooks, allowing us to emit a single expression at
    ///   the end (an array consisting of all hooks with their index associated)
    ///
    /// NOTE: I suspect this is grosser than it needs to be, but it works and really isn't fun to
    /// modify.
    macro_rules! hook_counter {
        // The accumulator has fully collected all of our hooks, so we can now emit a vec of them.
        ( [$( ($target:literal, $wrapper:ident, $counter:expr) ),*  $(,)?], $_counter:expr) => {
            [$( Hook {
                target: $target,
                wrapper: $wrapper::<{ $counter }>,
                original: OnceLock::new(),
            }),*]
        };
        // Handle the first iteration specifically
        ( [ ], $counter:expr, $target:literal, $wrapper:ident, $($rest:tt),*) => {
            hook_counter!( [
                ($target, $wrapper, $counter)
            ], $counter +1, $($rest),*)
        };
        // Handle the last iteration specifically, since we'll switch out of the normal recursive
        // case and into our accumulator case.
        ( [$($acc:tt),*  $(,)?], $counter:expr, $target:literal, $wrapper:ident) => {
            hook_counter!( [
                $($acc),*, ($target, $wrapper, $counter)
            ], $counter +1)
        };
        // The main recursive case
        ( [ $( $acc:tt ),* $(,)?], $counter:expr, $target:literal, $wrapper:ident, $($rest:tt),*) => {
            hook_counter!( [
                $($acc),*, ($target, $wrapper, $counter)
            ], $counter +1, $($rest),*)
        };
    }

    /// Generate an array of [`Hook`]s.  In particular, we need to generate unique references into
    /// [`HOOKS`] that each wrapper is aware of, meaning we need to use a custom push-down
    /// accumulator and counting macro.
    macro_rules! hooks {
        ($(($target:literal, $wrapper:ident)),* $(,)?) => {
            hook_counter!([], 0, $($target, $wrapper),*)
        };
    }

    /// The set of functions we'll be hooking.
    ///
    /// NOTE: This must be created by [`hooks`], since we actually generate new variants of the
    /// wrapper function for each hook, allowing the function to determine which hook triggered it
    /// at runtime.
    static HOOKS: [Hook; 11] = hooks!(
        ("builtins.print", logging_print),
        ("logging.debug", logging_print),
        ("logging.log", logging_print),
        ("logging.info", logging_print),
        ("logging.warning", logging_print),
        ("logging.error", logging_print),
        ("logging.critical", logging_print),
        ("logging.fatal", logging_print),
        ("logging.exception", logging_print),
        ("multiprocessing.util._exit_function", multiprocessing_exit),
        ("builtins.__import__", logging_import),
    );

    /// Information, used during both runtime and at [`install`] time, about a specific function
    /// that's being hooked.
    struct Hook {
        /// The hooking target, in a `<module>.<method>` format.
        target: &'static str,
        /// The Rust wrapper function, which proxies its arguments to `original` and returns its
        /// result.
        wrapper: extern "C" fn(*mut PyObject, *mut PyObject, *mut PyObject) -> *mut PyObject,
        /// The original Python function that's being wrapped.
        original: OnceLock<Py<PyAny>>,
    }

    /// A generic wrapper that parses out the arguments, calls the given handler function to handle
    /// custom hooking logic, then proxies the arguments out to the original wrapped function.
    fn proxy(
        hook: &Hook,
        handler: impl FnOnce(
            &Bound<'_, pyo3::types::PyTuple>,
        ) -> Option<function_trace::FunctionTrace<'static>>,
        args: *mut PyObject,
        kwargs: *mut PyObject,
    ) -> *mut PyObject {
        let orig = hook
            .original
            .get()
            .expect("Wrapper functions can't be called until hooked");

        let proxied = Python::with_gil(|py| -> Result<()> {
            if let Some(mut writer) = crate::_functiontrace_rs::thread_state() {
                let args = unsafe {
                    // SAFETY: `args` represents a valid argument tuple
                    Bound::from_borrowed_ptr(py, args)
                };
                let args = args
                    .downcast()
                    .map_err(Into::<PyErr>::into)
                    .wrap_err("Python args must be a tuple")?;

                if let Some(msg) = handler(args) {
                    msg.serialize(&mut rmp_serde::encode::Serializer::new(&mut writer))
                        .wrap_err("Failed to emit Allocation message")?;
                }
            }

            Ok(())
        })
        .wrap_err_with(|| format!("FunctionTrace proxy logging for {} failed", hook.target));

        if let Err(e) = proxied {
            tracing::error!(
                error = e.to_string(),
                function = hook.target,
                "Failed to properly handle hooked function"
            );
        }

        unsafe {
            // SAFETY: This is a direct translation of the original call we're proxying
            pyo3::ffi::PyObject_Call(orig.as_ptr(), args, kwargs)
        }
    }

    ////////////////////////////////////////////////////////////////////////////
    // Hook Implementations
    ////////////////////////////////////////////////////////////////////////////
    // NOTE: Each hook needs to be able to determine which index of `HOOKS` it corresponds to, so
    // must take a `<const HOOK: usize>` as the only generic argument.

    /// Given a log-like function, emit a [`FunctionTrace::Log`] event for it.
    extern "C" fn logging_print<const HOOK: usize>(
        _self: *mut PyObject,
        args: *mut PyObject,
        kwargs: *mut PyObject,
    ) -> *mut PyObject {
        let hook = &HOOKS[HOOK];

        proxy(
            hook,
            |args| {
                // Logging functions should roughly call `str()` on their arguments
                // TODO: We shouldn't need to explicitly allocate for this.
                let args = args
                    .str()
                    .and_then(|x| x.to_str().map(|x| Cow::Owned(x.to_string())))
                    .unwrap_or(Cow::Borrowed("<invalid string>"));

                Some(function_trace::FunctionTrace::Log {
                    time: trace_time(),
                    log_type: Cow::Borrowed(hook.target),
                    log_value: args,
                })
            },
            args,
            kwargs,
        )
    }

    /// Emit a [`FunctionTrace::Import`] event for `import` calls
    extern "C" fn logging_import<const HOOK: usize>(
        _self: *mut PyObject,
        args: *mut PyObject,
        kwargs: *mut PyObject,
    ) -> *mut PyObject {
        let hook = &HOOKS[HOOK];

        proxy(
            hook,
            |args| {
                // `import` takes rather complicated arguments, but in practice we only care about
                // the first argument (name)
                let module = if let Ok(arg) = args.get_item(0) {
                    arg.downcast()
                        .map_err(Into::into)
                        .and_then(|module| module.to_str())
                        .map(|module| Cow::Owned(module.to_string()))
                        .unwrap_or(Cow::Borrowed("<unknown module>"))
                } else {
                    Cow::Borrowed("<no module specified>")
                };

                Some(function_trace::FunctionTrace::Import {
                    time: trace_time(),
                    module_name: module,
                })
            },
            args,
            kwargs,
        )
    }

    /// Though this is mixed in with the rest of the hooks, this is actually load-bearing for
    /// general FunctionTrace functionality.
    ///
    /// `atexit()` will only run in the main process, so we need to register a separate
    /// multiprocessesing exit hook to do similar teardown on any multiprocessing workers.
    extern "C" fn multiprocessing_exit<const HOOK: usize>(
        _self: *mut PyObject,
        args: *mut PyObject,
        kwargs: *mut PyObject,
    ) -> *mut PyObject {
        let hook = &HOOKS[HOOK];

        if let Some(writer) = crate::_functiontrace_rs::thread_state() {
            crate::_functiontrace_rs::thread_teardown(writer)
                .expect("Multiprocessing teardown should be successful");
        }

        // Directly pass the command on, since we don't need to log/etc for this.
        proxy(hook, |_args| None, args, kwargs)
    }
}
