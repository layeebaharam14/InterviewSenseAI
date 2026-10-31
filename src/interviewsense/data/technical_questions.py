"""
technical_questions.py
Structured Technical Question Bank and Generation Engine for InterviewSense AI.
Supports 12 domains across Beginner, Intermediate, and Advanced tiers.
"""

import random
import re
from typing import List, Dict, Any

# ============================================================================
# TECHNICAL QUESTION BANK
# ============================================================================
QUESTION_BANK = {
    "Python Programming": {
        "Python Basics": {
            "Beginner": [
                {
                    "question": "What are Python's key features and why is it considered an interpreted language?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain the difference between mutable and immutable data types in Python with examples.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between '==' and 'is' operators in Python?",
                    "question_type": "Practical"
                },
                {
                    "question": "How does dynamic typing work in Python compared to static typing?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Write a short code snippet to demonstrate string slicing and reversing in Python.",
                    "question_type": "Coding"
                }
            ],
            "Intermediate": [
                {
                    "question": "How do Python's pass-by-object-reference semantics work for mutable vs immutable arguments?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain Python's Global Interpreter Lock (GIL) and its implications on CPU-bound multithreading.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between shallow copy and deep copy in Python? How is each implemented?",
                    "question_type": "Practical"
                },
                {
                    "question": "How do list comprehensions differ in performance from traditional for-loops?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain the purpose of the `if __name__ == '__main__':` idiom in Python.",
                    "question_type": "Practical"
                }
            ],
            "Advanced": [
                {
                    "question": "How does Python's cyclic garbage collector resolve circular references between objects?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain how Python uses PyObject and type descriptor structs at the C-API level.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are memory views and the Python Buffer Protocol, and how do they enable zero-copy operations?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Describe the internal hash randomization mechanism in Python dicts and its cryptographic mitigation.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How can you optimize the memory footprint of millions of small Python objects using `__slots__`?",
                    "question_type": "Practical"
                }
            ]
        },
        "OOP in Python": {
            "Beginner": [
                {
                    "question": "What are the four pillars of OOP and how are classes created in Python?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the purpose of the `__init__` constructor method in Python?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between class variables and instance variables in Python?",
                    "question_type": "Practical"
                },
                {
                    "question": "Explain single inheritance in Python with a brief code example.",
                    "question_type": "Coding"
                },
                {
                    "question": "What is method overriding in Python and how does `super()` facilitate it?",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "Explain Method Resolution Order (MRO) in Python multiple inheritance and the C3 linearization algorithm.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between `@staticmethod`, `@classmethod`, and regular instance methods?",
                    "question_type": "Practical"
                },
                {
                    "question": "How does name mangling work with private attributes (`__var`) in Python classes?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain the concept of Duck Typing in Python with an example.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "When would you prefer composition over inheritance in Python software design?",
                    "question_type": "Scenario-based"
                }
            ],
            "Advanced": [
                {
                    "question": "What are metaclasses in Python and how do `__new__` and `__init__` differ during class creation?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does the descriptor protocol (`__get__`, `__set__`, `__delete__`) power properties and methods?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How would you implement an Abstract Base Class (ABC) with strict interface validation?",
                    "question_type": "Coding"
                },
                {
                    "question": "How can you implement a thread-safe Singleton pattern in Python using a custom metaclass?",
                    "question_type": "Practical"
                },
                {
                    "question": "Explain the `__init_subclass__` hook introduced in PEP 487 as a lightweight alternative to metaclasses.",
                    "question_type": "Conceptual"
                }
            ]
        },
        "Functions and Modules": {
            "Beginner": [
                {
                    "question": "What is the difference between positional arguments and keyword arguments in Python?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do `*args` and `**kwargs` work in Python function definitions?",
                    "question_type": "Practical"
                },
                {
                    "question": "What are lambda functions in Python, and when should you avoid them?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do you create and import custom modules and packages in Python?",
                    "question_type": "Practical"
                },
                {
                    "question": "Explain local vs global variable scope in Python functions.",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "Explain closures in Python and how lexical scoping enables state retention across invocations.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is a decorator in Python? Write a decorator to log execution time of a function.",
                    "question_type": "Coding"
                },
                {
                    "question": "How do generator functions using `yield` differ from regular functions returning lists?",
                    "question_type": "Practical"
                },
                {
                    "question": "Explain the difference between `global` and `nonlocal` keywords in nested function scopes.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does Python resolve circular imports, and how can they be prevented in large projects?",
                    "question_type": "Problem-solving"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain coroutines under PEP 342 and how `yield from` evolved into modern `async`/`await`.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Implement a parameterized decorator that accepts arguments and preserves function signatures using `functools.wraps`.",
                    "question_type": "Coding"
                },
                {
                    "question": "How does Python's import system work under the hood via `sys.modules`, finders, and loaders?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does partial function application work using `functools.partial`, and what are its memory implications?",
                    "question_type": "Practical"
                },
                {
                    "question": "Design an LRU cache decorator from scratch with time-to-live (TTL) expiration.",
                    "question_type": "Problem-solving"
                }
            ]
        },
        "Exception Handling": {
            "Beginner": [
                {
                    "question": "Explain the basic syntax and control flow of `try`, `except`, `else`, and `finally` blocks.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between syntax errors and runtime exceptions in Python?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do you catch multiple distinct exceptions in a single `except` block?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is the purpose of the `raise` keyword in Python?",
                    "question_type": "Coding"
                },
                {
                    "question": "Why is catching `Exception` generally preferred over a bare `except:` clause?",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "How do you create a custom user-defined Exception class in Python with custom error messages?",
                    "question_type": "Coding"
                },
                {
                    "question": "What is exception chaining using `raise ... from ...` in Python 3?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain how the context management protocol (`__enter__`, `__exit__`) handles exceptions.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How can you capture and log full stack traces using the `logging` module without crashing?",
                    "question_type": "Practical"
                },
                {
                    "question": "What are common antipatterns in Python exception handling and how do they lead to silent bugs?",
                    "question_type": "Scenario-based"
                }
            ],
            "Advanced": [
                {
                    "question": "How do `ExceptionGroup` and `except*` in Python 3.11 handle concurrent task exceptions?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain `sys.exc_info()` and how Python tracks exception tracebacks across stack frames.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How can you safely suppress specific exceptions without side effects using `contextlib.suppress`?",
                    "question_type": "Practical"
                },
                {
                    "question": "Discuss reference cycle memory leak risks associated with saving exception tracebacks in objects.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Implement a resilient retry decorator with exponential backoff and jitter for transient API failures.",
                    "question_type": "Coding"
                }
            ]
        },
        "File Handling": {
            "Beginner": [
                {
                    "question": "What are the standard file access modes ('r', 'w', 'a', 'rb', 'wb') in Python?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Why is using the `with open(...)` context manager considered a best practice for file I/O?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between `read()`, `readline()`, and `readlines()` in Python?",
                    "question_type": "Practical"
                },
                {
                    "question": "How do you write text to a file without overwriting existing contents?",
                    "question_type": "Coding"
                },
                {
                    "question": "How do you check if a file exists before attempting to open it in Python?",
                    "question_type": "Practical"
                }
            ],
            "Intermediate": [
                {
                    "question": "How do you serialize and deserialize complex data structures using the `json` module?",
                    "question_type": "Practical"
                },
                {
                    "question": "Explain the difference between text mode and binary mode file operations in Python.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does `pathlib.Path` improve over legacy `os.path` functions?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How would you stream and process a 20GB log file in Python without running out of RAM?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What are the security and versioning risks associated with Python's `pickle` module?",
                    "question_type": "Scenario-based"
                }
            ],
            "Advanced": [
                {
                    "question": "How does memory-mapped file I/O work in Python using the `mmap` module?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain non-blocking asynchronous file operations with `aiofiles` and OS filesystem thread pools.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do you implement atomic file writes in Python to guarantee data integrity across unexpected crashes?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Describe low-level file descriptor operations and cross-platform file locking techniques.",
                    "question_type": "Practical"
                },
                {
                    "question": "Implement a chunked streaming file upload handler that computes an MD5 or SHA256 checksum on the fly.",
                    "question_type": "Coding"
                }
            ]
        },
        "Lists, Tuples, Sets and Dictionaries": {
            "Beginner": [
                {
                    "question": "What are the primary differences between Python lists and tuples?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What requirements must an object satisfy to be used as a dictionary key in Python?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do set mathematical operations (union, intersection, difference) work in Python?",
                    "question_type": "Practical"
                },
                {
                    "question": "Write a snippet to remove duplicates from a list while maintaining element order.",
                    "question_type": "Coding"
                },
                {
                    "question": "What exception occurs when looking up a missing key in a dict, and how can `.get()` prevent it?",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "What is the time complexity of lookup, insertion, and deletion in a list vs a dictionary?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do `collections.defaultdict` and `collections.Counter` simplify data grouping and counting?",
                    "question_type": "Practical"
                },
                {
                    "question": "How has Python dictionary insertion order preservation been implemented since Python 3.7?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain the difference between `list.sort()` in-place and the built-in `sorted()` function.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do set comprehensions and dictionary comprehensions work? Provide practical examples.",
                    "question_type": "Coding"
                }
            ],
            "Advanced": [
                {
                    "question": "Describe the internal architecture of Python's compact hash table implementation (indices vs entries).",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does dynamic array over-allocation work during `list.append()` to guarantee amortized O(1) time?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Implement an LRU Cache from scratch using a doubly linked list and a hash map.",
                    "question_type": "Coding"
                },
                {
                    "question": "How do `frozenset` objects differ from standard sets in terms of internal hashing and usage?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain hash collision resolution in Python dictionaries using open addressing with pseudo-random perturbation.",
                    "question_type": "Conceptual"
                }
            ]
        },
        "Libraries and Packages": {
            "Beginner": [
                {
                    "question": "What is pip and how does it resolve and install packages from PyPI?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the purpose of a requirements.txt file and how do you generate one with pip freeze?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is a virtual environment (venv) and why is it essential for dependency isolation?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the purpose of the `__init__.py` file in Python package directories?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do you inspect the installed version and metadata of a Python package programmatically?",
                    "question_type": "Practical"
                }
            ],
            "Intermediate": [
                {
                    "question": "Explain semantic versioning and dependency pinning constraints in requirements files.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between a wheel distribution (`.whl`) and a source distribution (`sdist`)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does `pyproject.toml` modernize project configuration and build requirements under PEP 517/518?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are implicit namespace packages in Python (PEP 420) and how do they function without `__init__.py`?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do modern dependency solvers like Poetry or uv resolve version lock graphs differently from pip?",
                    "question_type": "Scenario-based"
                }
            ],
            "Advanced": [
                {
                    "question": "How do C-extensions and Cython bridge compiled C/C++ code into Python for intense numerical computation?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain how Python dynamically loads shared libraries via `ctypes` and `cffi`.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How can you audit Python dependencies for known CVE security vulnerabilities in a CI/CD pipeline?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Describe the process of publishing an open-source library to PyPI using Twine and GitHub Actions.",
                    "question_type": "Practical"
                },
                {
                    "question": "What are manylinux platform tags and how do they ensure binary wheel compatibility across Linux distros?",
                    "question_type": "Conceptual"
                }
            ]
        }
    },
    "Java Programming": {
        "Core Java": {
            "Beginner": [
                {
                    "question": "What is the difference between JDK, JRE, and JVM in Java?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Why is Java described as platform-independent and 'Write Once, Run Anywhere'?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are primitive data types in Java and how do they differ from wrapper classes?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the role of `public static void main(String[] args)` in Java execution?",
                    "question_type": "Practical"
                },
                {
                    "question": "Explain the difference between `final`, `finally`, and `finalize()` in Java.",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "How does Java memory allocation divide between Stack and Heap?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is String interning and how does the String Constant Pool optimize memory?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain the contract between `equals()` and `hashCode()` in Java.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is the difference between `StringBuilder` and `StringBuffer`?",
                    "question_type": "Practical"
                },
                {
                    "question": "How does autoboxing and unboxing work in Java, and what pitfalls can cause NullPointerExceptions?",
                    "question_type": "Scenario-based"
                }
            ],
            "Advanced": [
                {
                    "question": "How does the JVM Just-In-Time (JIT) compiler perform Tiered Compilation and Escape Analysis?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain class loading architecture in Java: Bootstrap, Extension/Platform, and Application classloaders.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the Java Memory Model (JMM) and what does 'happens-before' guarantee?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do modern garbage collectors like G1GC and ZGC minimize stop-the-world pauses?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain Java reflection and how dynamic proxies work at runtime.",
                    "question_type": "Practical"
                }
            ]
        },
        "OOP Concepts": {
            "Beginner": [
                {
                    "question": "What is encapsulation in Java and how do access modifiers (private, protected, public) enforce it?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between method overloading and method overriding in Java?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the `super` keyword used for in Java subclasses?",
                    "question_type": "Practical"
                },
                {
                    "question": "Can you instantiate an abstract class in Java? Why or why not?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is polymorphism in Java? Explain compile-time vs runtime polymorphism.",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "What is the difference between an abstract class and an interface in Java (including Java 8 default methods)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Why does Java not support multiple inheritance with classes, and how does it avoid the diamond problem?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain dynamic method dispatch and how the JVM resolves overridden methods at runtime.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does the Liskov Substitution Principle (LSP) apply to object-oriented Java design?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "What is a marker interface in Java? Give two real-world examples.",
                    "question_type": "Practical"
                }
            ],
            "Advanced": [
                {
                    "question": "How does invokedynamic bytecode instruction revolutionize method invocation for lambda expressions in Java?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain the composition vs inheritance debate in high-throughput enterprise systems with design patterns.",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "How does sealed classes and interfaces feature introduced in Java 17 enforce exhaustive domain modeling?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Implement an immutable value object class in Java following defensive copying rules.",
                    "question_type": "Coding"
                },
                {
                    "question": "Explain the vtable (virtual method table) mechanism used by JVM for virtual dispatch.",
                    "question_type": "Conceptual"
                }
            ]
        },
        "Collections Framework": {
            "Beginner": [
                {
                    "question": "What is the Java Collections Framework and what are its core interfaces (List, Set, Map, Queue)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between an ArrayList and a LinkedList in Java?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does a HashSet ensure that no duplicate elements are stored?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between HashMap and TreeMap?",
                    "question_type": "Practical"
                },
                {
                    "question": "How do you iterate over a collection using an Iterator vs a for-each loop?",
                    "question_type": "Practical"
                }
            ],
            "Intermediate": [
                {
                    "question": "How does HashMap work internally in Java? Explain hashing, bucketing, and red-black tree conversion (treeification).",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What causes a ConcurrentModificationException and what are fail-fast vs fail-safe iterators?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is the difference between Comparable and Comparator interfaces in Java?",
                    "question_type": "Practical"
                },
                {
                    "question": "How does ConcurrentHashMap achieve thread safety without locking the entire map like Hashtable?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is PriorityQueue in Java and how does it implement a binary heap?",
                    "question_type": "Conceptual"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain the internal striping and CAS (Compare-And-Swap) mechanisms in ConcurrentHashMap.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does CopyOnWriteArrayList work under high read vs high write concurrency?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Design a custom bounded BlockingQueue using intrinsic monitors (wait/notify) or explicit ReentrantLock + Condition.",
                    "question_type": "Coding"
                },
                {
                    "question": "What are Spliterators in Java and how do they enable parallel stream partitioning?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Analyze memory overhead and cache locality differences between primitive arrays and boxed Collection classes.",
                    "question_type": "Conceptual"
                }
            ]
        },
        "Exception Handling": {
            "Beginner": [
                {
                    "question": "What is the hierarchy of Throwable, Exception, and Error in Java?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between checked exceptions and unchecked (runtime) exceptions in Java?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain the purpose of the try-catch-finally construct in Java.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between throw and throws keywords in Java?",
                    "question_type": "Practical"
                },
                {
                    "question": "Can a finally block execute if System.exit(0) is called in the try block?",
                    "question_type": "Problem-solving"
                }
            ],
            "Intermediate": [
                {
                    "question": "How does the try-with-resources statement in Java work with the AutoCloseable interface?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is exception suppression in Java try-with-resources blocks?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do you design and structure custom checked vs unchecked exceptions in a microservice application?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Can you catch multiple exceptions using multi-catch syntax (`catch (IOException | SQLException e)`)?",
                    "question_type": "Practical"
                },
                {
                    "question": "What happens if both try block and finally block return a value in Java?",
                    "question_type": "Problem-solving"
                }
            ],
            "Advanced": [
                {
                    "question": "What is the performance overhead of creating exceptions in Java due to `fillInStackTrace()`?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How can you implement lightweight, stackless exceptions for high-frequency control-flow validation in Java?",
                    "question_type": "Coding"
                },
                {
                    "question": "Discuss exception propagation across asynchronous CompletableFuture pipeline chains.",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "How does the JVM handle OOM (OutOfMemoryError: Java heap space vs Metaspace) and how can you diagnose it via heap dumps?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain how global exception handler middleware operates in Spring Boot using `@ControllerAdvice` and `@ExceptionHandler`.",
                    "question_type": "Practical"
                }
            ]
        },
        "Multithreading": {
            "Beginner": [
                {
                    "question": "What is a thread in Java and what are the two primary ways to create a thread?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are the different lifecycle states of a thread in Java (Thread.State)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between `start()` and `run()` methods in Thread?",
                    "question_type": "Practical"
                },
                {
                    "question": "What does `Thread.sleep()` do, and what exception must be handled when calling it?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the purpose of the `synchronized` keyword in Java?",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "What is the difference between `wait()`, `notify()`, and `notifyAll()`, and why must they be called inside synchronized context?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain volatile variable visibility in Java and how it prevents instruction reordering.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is thread starvation, race condition, and deadlock? Give an example of how deadlock occurs.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How does the ExecutorService framework decouple task submission from task execution in Java?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is the difference between Callable and Runnable interfaces in Java?",
                    "question_type": "Conceptual"
                }
            ],
            "Advanced": [
                {
                    "question": "How does AbstractQueuedSynchronizer (AQS) form the foundation of java.util.concurrent locks?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain Virtual Threads introduced in Project Loom (Java 21) and how they differ from platform threads.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do AtomicInteger and other atomic variables use CAS operations without explicit locking?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain the Fork/Join framework and work-stealing algorithm in Java.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Implement a thread-safe connection pool using Semaphore and ConcurrentLinkedQueue.",
                    "question_type": "Coding"
                }
            ]
        },
        "JDBC": {
            "Beginner": [
                {
                    "question": "What is JDBC and what role does a JDBC driver play in Java database connectivity?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are the core interfaces in JDBC (Connection, Statement, PreparedStatement, ResultSet)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Why should you use PreparedStatement instead of Statement in JDBC?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "How do you close JDBC connections and statements properly to prevent resource leaks?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is the function of `DriverManager.getConnection()` in Java?",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "How do database connection pools like HikariCP improve JDBC application performance?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain transaction management in JDBC: `setAutoCommit(false)`, `commit()`, and `rollback()`.",
                    "question_type": "Practical"
                },
                {
                    "question": "What is JDBC batch processing using `addBatch()` and `executeBatch()`, and when should it be used?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What are Savepoints in JDBC transactions?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do you handle SQL NULL values properly when reading from a ResultSet?",
                    "question_type": "Practical"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain how JDBC driver types (Type 1 to Type 4) differ in architecture, performance, and portability.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does statement caching work in JDBC connection pools and database servers?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How do distributed two-phase commit transactions (XA / JTA) work across multiple JDBC data sources?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Analyze row-fetching strategies and `fetchSize` parameter optimizations when streaming millions of records via JDBC.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What are isolation levels in JDBC transactions and what concurrency anomalies does each prevent?",
                    "question_type": "Conceptual"
                }
            ]
        },
        "Java 8 Features": {
            "Beginner": [
                {
                    "question": "What are Lambda Expressions in Java 8 and how do they reduce boilerplate code?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is a Functional Interface in Java? Name three standard functional interfaces in java.util.function.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the purpose of default and static methods in Java 8 interfaces?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is method reference (`::`) syntax in Java 8?",
                    "question_type": "Practical"
                },
                {
                    "question": "What problem does the Optional class solve in Java 8?",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "Explain the Java 8 Stream API: what is the difference between intermediate and terminal operations?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do `map()`, `filter()`, `flatMap()`, and `reduce()` work in Java Streams? Provide an example.",
                    "question_type": "Coding"
                },
                {
                    "question": "What is the difference between sequential streams and parallel streams in Java 8?",
                    "question_type": "Practical"
                },
                {
                    "question": "How does Java 8 Date and Time API (`java.time.LocalDate`, Instant, Duration) improve over `java.util.Date`?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does `Collectors.groupingBy()` work in stream processing pipelines?",
                    "question_type": "Problem-solving"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain stream laziness and short-circuiting evaluation under the hood in Java 8.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does CompletableFuture in Java 8 enable non-blocking asynchronous programming and composition?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Write a custom collector implementing the `java.util.stream.Collector` interface.",
                    "question_type": "Coding"
                },
                {
                    "question": "Discuss the internal lambda translation mechanism using invokedynamic and LambdaMetafactory.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Analyze the overhead of boxing/unboxing in streams and when to use primitive specializations (IntStream, LongStream).",
                    "question_type": "Problem-solving"
                }
            ]
        }
    },
    "C Programming": {
        "C Basics": {
            "Beginner": [
                {
                    "question": "Explain the compilation process of a C program: Preprocessing, Compiling, Assembling, and Linking.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are header files and what does `#include <stdio.h>` do?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are the basic data types in C and their standard memory sizes?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between `printf()` and `scanf()`?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is the significance of the return value in `int main()`?",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "What are storage classes in C (`auto`, `register`, `static`, `extern`) and their scopes/lifetimes?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain the difference between macro substitution (`#define`) and `const` variables in C.",
                    "question_type": "Practical"
                },
                {
                    "question": "What is type casting in C? Explain implicit type promotion vs explicit casting.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between signed and unsigned integers and how does integer overflow behave?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How does short-circuit evaluation work with logical operators (`&&`, `||`) in C?",
                    "question_type": "Practical"
                }
            ],
            "Advanced": [
                {
                    "question": "What is Undefined Behavior (UB) in C? Give three real-world examples and compiler optimization consequences.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain memory alignment, struct padding, and the `#pragma pack` directive.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What does the `volatile` keyword prevent when compiling embedded or device driver code in C?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain how sequence points and order of evaluation impact expressions like `i = i++ + ++i`.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How does inline assembly (`__asm__`) function within C code for platform-specific hardware instructions?",
                    "question_type": "Practical"
                }
            ]
        },
        "Pointers": {
            "Beginner": [
                {
                    "question": "What is a pointer in C and what do the `&` (address-of) and `*` (dereference) operators do?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is a NULL pointer and why should pointers be initialized before use?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is pointer arithmetic and how does incrementing a pointer (`ptr++`) depend on data type size?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is a void pointer (`void *`) in C and how can it be dereferenced?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Write a C function to swap two integers using pointers.",
                    "question_type": "Coding"
                }
            ],
            "Intermediate": [
                {
                    "question": "What is the difference between a pointer to a constant (`const int *`) and a constant pointer (`int * const`)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are dangling pointers and wild pointers in C? How do they cause crashes or security bugs?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is a double pointer (`**ptr`) and when is it necessary (e.g. modifying head pointer in linked list)?",
                    "question_type": "Practical"
                },
                {
                    "question": "What are function pointers in C? Write a snippet declaring and calling a function pointer.",
                    "question_type": "Coding"
                },
                {
                    "question": "Explain the relationship between 1D arrays and pointers in C expressions.",
                    "question_type": "Conceptual"
                }
            ],
            "Advanced": [
                {
                    "question": "How do callback architectures and virtual function tables get constructed in C using arrays of function pointers?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain strict aliasing rules in C and how `char *` and `restrict` keyword affect compiler optimizations.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Analyze the assembly instructions generated for dereferencing near vs far pointers and memory barriers.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How can you detect buffer overflows and pointer corruption using canary tokens and address sanitizers?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Implement a generic quicksort function in C accepting a custom comparator function pointer.",
                    "question_type": "Coding"
                }
            ]
        },
        "Arrays and Strings": {
            "Beginner": [
                {
                    "question": "How are arrays declared and initialized in C, and how is their size calculated using `sizeof`?",
                    "question_type": "Practical"
                },
                {
                    "question": "How are strings represented in C and what is the role of the null terminator (`\\0`)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between `char str[] = \"hello\";` and `char *str = \"hello\";`?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What do standard string functions (`strlen`, `strcpy`, `strcat`, `strcmp`) do in `<string.h>`?",
                    "question_type": "Practical"
                },
                {
                    "question": "Write a function to calculate the length of a string without using library functions.",
                    "question_type": "Coding"
                }
            ],
            "Intermediate": [
                {
                    "question": "Why is `gets()` dangerous and deprecated, and how does `fgets()` provide buffer overflow protection?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "How are 2D arrays laid out in memory in C (Row-Major Order)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Write a C function to reverse a string in-place without using extra memory buffers.",
                    "question_type": "Coding"
                },
                {
                    "question": "What is the difference between safe string functions like `strncpy` vs `snprintf`?",
                    "question_type": "Practical"
                },
                {
                    "question": "How do you pass multi-dimensional arrays to functions in C?",
                    "question_type": "Coding"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain Variable Length Arrays (VLAs) in C99 and why they can lead to stack overflow vulnerabilities.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Implement an optimized `memcpy` and `memmove` function handling overlapping memory buffers correctly.",
                    "question_type": "Coding"
                },
                {
                    "question": "Analyze cache line utilization and stride performance when traversing row-major vs column-major matrices in C.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How do string interning and read-only text segment sections (`.rodata`) operate at the ELF binary level?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Implement an efficient string tokenizer in C without modifying the original source string.",
                    "question_type": "Coding"
                }
            ]
        },
        "Structures and Unions": {
            "Beginner": [
                {
                    "question": "What is a `struct` in C and how do you define and access its members?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between the `.` (dot) and `->` (arrow) operators?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is the difference between a `struct` and a `union` in C in terms of memory allocation?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does the `typedef` keyword simplify struct declarations?",
                    "question_type": "Practical"
                },
                {
                    "question": "Can a struct contain a pointer to another struct of the same type? What is this called?",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "What are bit-fields in C structures and how do they optimize hardware register mapping?",
                    "question_type": "Practical"
                },
                {
                    "question": "Explain structure padding and structure packing with memory alignment rules.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does the `offsetof` macro in `<stddef.h>` work to compute member offsets?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Can structures be passed to functions by value and returned by value? What are the performance costs?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "How do tagged unions (discriminated unions) implement polymorphic state representations in C?",
                    "question_type": "Coding"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain how Linux kernel's `container_of()` macro recovers enclosing struct pointers from member pointers.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do flexible array members in C99 structs allow variable-sized payload allocations?",
                    "question_type": "Coding"
                },
                {
                    "question": "Discuss serialization and endianness conversion when transmitting binary structs over network sockets.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Analyze structure layout cache alignment and false sharing issues in multi-threaded C applications.",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Design an extensible type-safe event dispatcher in C using opaque struct pointers.",
                    "question_type": "Coding"
                }
            ]
        },
        "Functions": {
            "Beginner": [
                {
                    "question": "What is a function prototype in C and why is it necessary before calling a function?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain call by value vs call by reference in C.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is recursion and what is the base condition in a recursive function?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Write a recursive C function to calculate the factorial of a positive integer.",
                    "question_type": "Coding"
                },
                {
                    "question": "What happens if a non-void function does not explicitly return a value in C?",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "What is stack frame anatomy during a function call in C (return address, arguments, saved registers)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are inline functions (`inline` keyword) in C99 and how do they compare with preprocessor macros?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do variadic functions work in C using `<stdarg.h>` (`va_list`, `va_start`, `va_arg`, `va_end`)?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is tail call recursion and how can optimizing compilers convert it into iteration to save stack space?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How do static functions in C achieve module-level file scope encapsulation?",
                    "question_type": "Conceptual"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain calling conventions in x86/x64 architecture (cdecl, stdcall, fastcall, System V AMD64 ABI).",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does buffer overflow exploit stack frame return addresses to achieve arbitrary code execution?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Implement a custom `printf`-like formatting function in C that parses `%d`, `%s`, and `%c` specifiers.",
                    "question_type": "Coding"
                },
                {
                    "question": "What are non-local jumps in C using `setjmp()` and `longjmp()`, and how do they implement exception handling?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain compiler attributes like `__attribute__((noreturn))` and `__attribute__((constructor))` in GCC/Clang.",
                    "question_type": "Conceptual"
                }
            ]
        },
        "Memory Management": {
            "Beginner": [
                {
                    "question": "What is the difference between static, stack, and heap memory allocation in C?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What do `malloc()`, `calloc()`, `realloc()`, and `free()` do in C?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between `malloc(n * sizeof(int))` and `calloc(n, sizeof(int))`?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is a memory leak and what happens if you forget to call `free()`?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Why is it important to set a pointer to `NULL` immediately after freeing it?",
                    "question_type": "Practical"
                }
            ],
            "Intermediate": [
                {
                    "question": "What causes a segmentation fault (`SIGSEGV`) and a bus error (`SIGBUS`) in C?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is double free error and how does it compromise heap metadata integrity?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does `realloc()` work when extending memory in-place vs reallocating to a new memory block?",
                    "question_type": "Practical"
                },
                {
                    "question": "What tools can you use to diagnose memory leaks and invalid read/writes in C programs (e.g. Valgrind, ASan)?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "What is heap fragmentation (internal vs external) and how does it degrade long-running server processes?",
                    "question_type": "Conceptual"
                }
            ],
            "Advanced": [
                {
                    "question": "How does a standard heap allocator (like dlmalloc or glibc ptmalloc) maintain free chunks, fastbins, and arenas?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Implement a custom memory pool / arena allocator in C for ultra-fast allocations without fragmentation.",
                    "question_type": "Coding"
                },
                {
                    "question": "Explain `brk()`, `sbrk()`, and `mmap()` system calls in Unix virtual memory allocation.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do slab allocation and buddy memory allocation algorithms function inside OS kernels?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Design a garbage collection prototype in C using reference counting or mark-and-sweep.",
                    "question_type": "Problem-solving"
                }
            ]
        },
        "File Handling": {
            "Beginner": [
                {
                    "question": "What is a `FILE` pointer in C and how do `fopen()` and `fclose()` work?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are standard file streams: `stdin`, `stdout`, and `stderr`?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain the difference between file modes \"w\", \"r\", and \"a\".",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do `fgetc()`, `fputc()`, `fgets()`, and `fputs()` operate on text files?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is EOF (End of File) and how do you check for it using `feof()`?",
                    "question_type": "Practical"
                }
            ],
            "Intermediate": [
                {
                    "question": "What is the difference between text mode and binary mode (\"rb\", \"wb\") file operations in C?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do `fread()` and `fwrite()` read and write binary structures to a file?",
                    "question_type": "Practical"
                },
                {
                    "question": "Explain random access in files using `fseek()`, `ftell()`, and `rewind()` with `SEEK_SET`, `SEEK_CUR`, and `SEEK_END`.",
                    "question_type": "Coding"
                },
                {
                    "question": "What is I/O buffering in C (`_IONBF`, `_IOLBF`, `_IOFBF`) and what does `fflush()` do?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do you handle file open errors and inspect `errno` using `perror()`?",
                    "question_type": "Practical"
                }
            ],
            "Advanced": [
                {
                    "question": "How do POSIX system calls (`open`, `read`, `write`, `close`, `lseek`) compare to C standard library buffered streams (`fopen`, `fread`)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How can you implement non-blocking asynchronous file I/O or direct I/O (`O_DIRECT`) in Linux C?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain file locking mechanisms (`fcntl` vs `flock`) to prevent race conditions across concurrent processes.",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Describe memory-mapped file access using `mmap()` and how dirty pages flush back to disk via `msync()`.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Implement an atomic file replacement utility in C that guarantees zero file corruption during power failures.",
                    "question_type": "Coding"
                }
            ]
        }
    },
    "C++ Programming": {
        "C++ Basics": {
            "Beginner": [
                {
                    "question": "How does C++ extend C, and what are namespaces in C++?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between `cin`/`cout` with `<iostream>` and `scanf`/`printf` with `<stdio.h>`?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is function overloading in C++ and how does the compiler distinguish between overloaded functions?",
                    "question_type": "Practical"
                },
                {
                    "question": "What are default arguments in C++ functions, and where must they be declared?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain the difference between `NULL` and `nullptr` introduced in C++11.",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "What is the difference between `auto` type deduction and `decltype` in modern C++?",
                    "question_type": "Practical"
                },
                {
                    "question": "What are range-based for loops in C++ and how do they work with iterators?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain `constexpr` and `consteval` and how they enable compile-time computation.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is an `enum class` (scoped enumeration) in C++11 and how does it prevent implicit conversions?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain operator overloading in C++. Which operators cannot be overloaded?",
                    "question_type": "Conceptual"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain value categories in C++: lvalue, rvalue, prvalue, and xvalue.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does C++ name mangling work at the ABI level and why is `extern \"C\"` required for C interoperability?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain structured binding declarations introduced in C++17.",
                    "question_type": "Practical"
                },
                {
                    "question": "Discuss memory order models in `<atomic>`: `memory_order_relaxed`, `memory_order_acquire`, `memory_order_release`, `memory_order_seq_cst`.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain user-defined literals in modern C++ and their type-safe advantages.",
                    "question_type": "Conceptual"
                }
            ]
        },
        "OOP Concepts": {
            "Beginner": [
                {
                    "question": "What are access specifiers (`public`, `protected`, `private`) in C++ classes and struct defaults?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are constructors and destructors in C++? When is a destructor called?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the `this` pointer in C++?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is a copy constructor in C++ and when is it implicitly invoked?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is virtual function and runtime polymorphism in C++?",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "Explain the Rule of Three, Rule of Five, and Rule of Zero in modern C++.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Why should base class destructors always be declared `virtual` in polymorphic hierarchies?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "What is a pure virtual function and an abstract class in C++?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain how multiple inheritance can lead to the Diamond Problem, and how virtual base classes resolve it.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is the difference between deep copy and shallow copy when objects contain raw dynamic pointers?",
                    "question_type": "Practical"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain the internal mechanism of the Virtual Table (`vtable`) and Virtual Pointer (`vptr`) in C++ dynamic dispatch.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the Curiously Recurring Template Pattern (CRTP) and how does it achieve static polymorphism without vtable overhead?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is object slicing in C++ when passing derived objects by value to base parameters?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Explain copy elision and Named Return Value Optimization (NRVO) guaranteed in modern C++ standards.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Design a class with deleted copy semantics (`= delete`) and explicit move semantics (`= default`).",
                    "question_type": "Coding"
                }
            ]
        },
        "Pointers and References": {
            "Beginner": [
                {
                    "question": "What is the difference between a pointer and a reference in C++?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Can a reference in C++ be NULL or reassigned to another variable after initialization?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do you pass arguments by reference (`int&`) to a function to avoid copying?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is a constant reference (`const T&`) and why is it preferred for passing large objects?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Write a short C++ snippet swapping two values using reference parameters.",
                    "question_type": "Coding"
                }
            ],
            "Intermediate": [
                {
                    "question": "What are Rvalue references (`T&&`) introduced in C++11, and how do they enable Move Semantics?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is `std::move` and what does it actually do to an object at runtime?",
                    "question_type": "Practical"
                },
                {
                    "question": "Explain perfect forwarding and `std::forward` in universal reference (forwarding reference) contexts.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What are smart pointers (`std::unique_ptr`, `std::shared_ptr`, `std::weak_ptr`) in `<memory>`?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does `std::weak_ptr` break cyclic reference memory leaks caused by `std::shared_ptr`?",
                    "question_type": "Scenario-based"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain the internal control block architecture of `std::shared_ptr` (strong ref count, weak ref count, allocator, deleter).",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Why is `std::make_shared` more cache-friendly and exception-safe than `std::shared_ptr(new T)`?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Analyze reference collapsing rules in C++ template parameter deduction (`& + &`, `& + &&`, `&& + &`, `&& + &&`).",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Implement a custom lightweight `UniquePtr` class following RAII and move-only semantics.",
                    "question_type": "Coding"
                },
                {
                    "question": "What is type aliasing with `reinterpret_cast` vs `static_cast` vs `dynamic_cast` vs `const_cast`?",
                    "question_type": "Conceptual"
                }
            ]
        },
        "STL": {
            "Beginner": [
                {
                    "question": "What is the C++ Standard Template Library (STL) and what are its four components: containers, algorithms, iterators, functors?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between `std::vector` and `std::array` in C++?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between `std::map` (ordered) and `std::unordered_map` (hash-based)?",
                    "question_type": "Practical"
                },
                {
                    "question": "What do `std::sort`, `std::find`, and `std::reverse` do in `<algorithm>`?",
                    "question_type": "Practical"
                },
                {
                    "question": "What are iterators in STL and what is the difference between `.begin()` and `.end()`?",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "What causes iterator invalidation in `std::vector` when elements are inserted or capacity is exceeded?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is the difference between `push_back()` and `emplace_back()` in modern C++ containers?",
                    "question_type": "Practical"
                },
                {
                    "question": "How is `std::map` implemented internally (Red-Black Tree) and what are its logarithmic performance guarantees?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are lambda expressions in modern C++? Explain capture clauses (`[]`, `[&]`, `[=]`).",
                    "question_type": "Coding"
                },
                {
                    "question": "How does `std::priority_queue` work as a max-heap and how do you configure it into a min-heap?",
                    "question_type": "Practical"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain custom hash functions and equality comparators for user-defined structs in `std::unordered_map`.",
                    "question_type": "Coding"
                },
                {
                    "question": "Analyze the memory layout, chunked paging, and random access performance of `std::deque` vs `std::vector`.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How do C++20 Ranges and Views pipeline operations (`| std::views::filter | std::views::transform`) without creating intermediate copies?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is Small String Optimization (SSO) in `std::string` and what are its stack size thresholds across major compilers?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Implement a high-performance custom memory allocator conforming to the C++ allocator requirements (`std::allocator_traits`).",
                    "question_type": "Coding"
                }
            ]
        },
        "Templates": {
            "Beginner": [
                {
                    "question": "What are templates in C++ and how do they enable generic programming?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between a function template and a class template in C++?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Write a generic function template to return the maximum of two values.",
                    "question_type": "Coding"
                },
                {
                    "question": "What are non-type template parameters (e.g. `template <typename T, size_t N> class Array`)?",
                    "question_type": "Practical"
                },
                {
                    "question": "Why are template definitions typically placed in header files rather than `.cpp` implementation files?",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "What is template specialization? Explain explicit (full) vs partial template specialization.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are Variadic Templates in C++11? Write a variadic template function to print variable arguments.",
                    "question_type": "Coding"
                },
                {
                    "question": "What is SFINAE (Substitution Failure Is Not An Error) and what problem does it solve in template metaprogramming?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does `std::enable_if` conditionally enable or disable template overloads?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain fold expressions introduced in C++17 for variadic template expansion.",
                    "question_type": "Practical"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain Concepts and Constraints introduced in C++20 (`requires` clause) and how they replace cumbersome SFINAE tricks.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is Template Metaprogramming (TMP) and how can compile-time factorial or type-trait computation be executed?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How do expression templates eliminate temporary object creation in numerical linear algebra libraries (like Eigen)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain template argument deduction guides (CTAD) in C++17.",
                    "question_type": "Practical"
                },
                {
                    "question": "Design a type trait `is_iterable<T>` using C++20 concepts or C++14 `std::void_t`.",
                    "question_type": "Coding"
                }
            ]
        },
        "Memory Management": {
            "Beginner": [
                {
                    "question": "What is the difference between `new`/`delete` in C++ and `malloc()`/`free()` in C?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between `delete` and `delete[]` in C++?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is RAII (Resource Acquisition Is Initialization) and why is it the core paradigm of C++ resource management?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is a memory leak and how do modern smart pointers prevent leaks?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What happens if dynamic memory allocation with `new` fails? Does it return NULL or throw an exception?",
                    "question_type": "Practical"
                }
            ],
            "Intermediate": [
                {
                    "question": "What is placement new in C++ and where is it used (e.g. custom memory arenas, `std::vector`)?",
                    "question_type": "Practical"
                },
                {
                    "question": "Explain the difference between `std::unique_ptr` and `std::shared_ptr` ownership models.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is custom deleter in smart pointers and how do you write a custom deleter for managing C-style resources (`FILE *`)?",
                    "question_type": "Coding"
                },
                {
                    "question": "What are dangling references and how can returning local references cause undefined behavior?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is the purpose of `std::nothrow` with the `new` operator?",
                    "question_type": "Conceptual"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain Polymorphic Memory Resources (`std::pmr`) introduced in C++17 for custom memory management.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do memory alignment and hardware cache line considerations affect structure packing and allocator design?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Implement an efficient fixed-size block pool allocator in C++ with zero runtime overhead.",
                    "question_type": "Coding"
                },
                {
                    "question": "Analyze the thread-safety guarantees of `std::shared_ptr` reference counter manipulation vs underlying object mutation.",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Discuss how memory sanitizers (ASan, LSan, MSan) detect invalid heap/stack access at compile-time instrumentation.",
                    "question_type": "Conceptual"
                }
            ]
        },
        "Exception Handling": {
            "Beginner": [
                {
                    "question": "Explain the syntax and purpose of `try`, `catch`, and `throw` blocks in C++.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is `catch (...)` (catch-all) and where should it be positioned in a catch hierarchy?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What standard exceptions are available in `<stdexcept>` (e.g. `runtime_error`, `out_of_range`, `invalid_argument`)?",
                    "question_type": "Practical"
                },
                {
                    "question": "How do you define a custom exception class by inheriting from `std::exception`?",
                    "question_type": "Coding"
                },
                {
                    "question": "What happens if an exception is thrown in a C++ program and never caught?",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "Explain Stack Unwinding in C++ and how RAII guarantees that local destructors run during exception propagation.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Why should destructors NEVER throw exceptions in C++? What happens if an exception escapes a destructor during stack unwinding?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "What does the `noexcept` specifier signify and how does it allow `std::vector` to use move operations instead of copy?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain exception safety guarantees: Basic guarantee, Strong guarantee, and Nothrow guarantee.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does copy-and-swap idiom provide the Strong Exception Safety guarantee in assignment operators?",
                    "question_type": "Coding"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain function-try-blocks on constructors and how they handle exceptions in base class or member initialization lists.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is `std::current_exception`, `std::exception_ptr`, and `std::rethrow_exception` for cross-thread exception marshaling?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Analyze the zero-cost exception handling model (Itanium DWARF CFI tables) vs return code checking overhead.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does `std::nested_exception` capture nested exception chains in modern C++?",
                    "question_type": "Practical"
                },
                {
                    "question": "Discuss alternatives to exceptions in high-frequency trading and embedded C++ systems (`std::expected` in C++23).",
                    "question_type": "Scenario-based"
                }
            ]
        }
    },
    "Data Structures and Algorithms": {
        "Arrays": {
            "Beginner": [
                {
                    "question": "What is an array and what are its memory layout characteristics?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Why does array indexing start at 0, and what is the time complexity of element access by index?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do you find the minimum and maximum elements in an unsorted array?",
                    "question_type": "Coding"
                },
                {
                    "question": "What is the difference between static arrays and dynamic arrays?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Write an algorithm to reverse an array in-place without using extra space.",
                    "question_type": "Coding"
                }
            ],
            "Intermediate": [
                {
                    "question": "Explain the Two-Pointer technique and solve the Two-Sum problem on a sorted array.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain Kadane\\'s algorithm for finding the maximum subarray sum in O(N) time.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How does the Sliding Window pattern optimize subarray problems from O(N^2) to O(N)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Write an algorithm to rotate an array by K positions to the right in O(N) time and O(1) space.",
                    "question_type": "Coding"
                },
                {
                    "question": "How do you find the single missing number in an array containing numbers from 1 to N?",
                    "question_type": "Problem-solving"
                }
            ],
            "Advanced": [
                {
                    "question": "How does the Dutch National Flag algorithm sort an array of 0s, 1s, and 2s in a single pass?",
                    "question_type": "Coding"
                },
                {
                    "question": "Explain the Trapping Rainwater problem and its two-pointer O(N) time O(1) space solution.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How do you solve the Longest Consecutive Sequence problem in O(N) time using a Hash Set?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain Boyer-Moore Voting Algorithm for finding majority elements in an array.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Solve the Next Permutation problem in O(N) time using lexicographical sequencing rules.",
                    "question_type": "Coding"
                }
            ]
        },
        "Linked Lists": {
            "Beginner": [
                {
                    "question": "What is a Linked List and how does it differ fundamentally from an Array?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are the structural differences between a Singly Linked List and a Doubly Linked List?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the time complexity to insert a node at the head vs at the tail of a linked list?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Write code to traverse and print all elements of a singly linked list.",
                    "question_type": "Coding"
                },
                {
                    "question": "What happens when you lose the reference to the head of a linked list?",
                    "question_type": "Problem-solving"
                }
            ],
            "Intermediate": [
                {
                    "question": "How do you reverse a singly linked list iteratively and recursively in O(N) time?",
                    "question_type": "Coding"
                },
                {
                    "question": "Explain Floyd\\'s Cycle Detection (Tortoise and Hare) algorithm to detect a loop in a linked list.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How do you find the middle node of a linked list in a single pass?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How do you remove the Nth node from the end of a linked list in one pass?",
                    "question_type": "Coding"
                },
                {
                    "question": "How do you merge two sorted linked lists into a single sorted linked list in O(N) time?",
                    "question_type": "Coding"
                }
            ],
            "Advanced": [
                {
                    "question": "How do you find the exact node where a cycle begins in a linked list using pointer arithmetic analysis?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain the algorithm to reverse nodes in a linked list in groups of K (Reverse Nodes in k-Group).",
                    "question_type": "Coding"
                },
                {
                    "question": "How do you merge K sorted linked lists efficiently using a min-heap in O(N log K) time?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How do you clone a linked list with next and random pointers in O(N) time and O(1) auxiliary space?",
                    "question_type": "Coding"
                },
                {
                    "question": "Design a Skip List and explain how probabilistic balancing achieves O(log N) search, insert, and delete.",
                    "question_type": "Conceptual"
                }
            ]
        },
        "Stacks and Queues": {
            "Beginner": [
                {
                    "question": "What is a Stack and why is it called a LIFO (Last In First Out) structure?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is a Queue and why is it called a FIFO (First In First Out) structure?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are the core operations of a stack and queue and what are their time complexities?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is stack overflow and stack underflow?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do you check for balanced parentheses in an expression string using a stack?",
                    "question_type": "Coding"
                }
            ],
            "Intermediate": [
                {
                    "question": "How do you implement a Queue using two Stacks, and what is the amortized cost per operation?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How do you design a Min-Stack that supports push, pop, top, and retrieving min in O(1) time?",
                    "question_type": "Coding"
                },
                {
                    "question": "Explain how Monotonic Stack solves the Next Greater Element problem in O(N) time.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is a Circular Queue and how does it prevent wasted array capacity?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do you evaluate a Postfix (Reverse Polish Notation) expression using a stack?",
                    "question_type": "Coding"
                }
            ],
            "Advanced": [
                {
                    "question": "Solve the Largest Rectangle in Histogram problem in O(N) time using a monotonic stack.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain how the Sliding Window Maximum problem is solved in O(N) time using a Monotonic Deque.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How do you implement a lock-free concurrent Queue using CAS operations (Michael-Scott queue algorithm)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Design a system to implement a cache-aware priority deque for ultra-low latency order matching.",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Explain the trapping rainwater problem using a stack-based approach.",
                    "question_type": "Problem-solving"
                }
            ]
        },
        "Trees and Graphs": {
            "Beginner": [
                {
                    "question": "What is a Binary Tree and how does it differ from a Binary Search Tree (BST)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain in-order, pre-order, and post-order depth-first traversals of a binary tree.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between a tree and a graph?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How is a graph represented using an Adjacency Matrix vs an Adjacency List?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Write an algorithm to calculate the maximum depth (height) of a binary tree.",
                    "question_type": "Coding"
                }
            ],
            "Intermediate": [
                {
                    "question": "Explain Breadth-First Search (BFS) and Depth-First Search (DFS) in graphs with their time/space complexities.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do you validate if a given binary tree is a valid Binary Search Tree (BST)?",
                    "question_type": "Coding"
                },
                {
                    "question": "Explain Lowest Common Ancestor (LCA) in a BST vs in a general Binary Tree.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How do you detect a cycle in a directed graph using DFS and recursion stack / color marking?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain Dijkstra\\'s shortest path algorithm and its time complexity using an adjacency list and min-heap.",
                    "question_type": "Conceptual"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain Topological Sorting and Kahn\\'s algorithm for DAGs with cycle detection.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What are self-balancing BSTs (AVL Trees and Red-Black Trees)? Explain tree rotations.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does the Disjoint Set Union (Union-Find) data structure achieve near-O(1) time using path compression and union by rank?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain Tarjan\\'s or Kosaraju\\'s algorithm to find Strongly Connected Components (SCCs) in a directed graph.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Design a Trie (Prefix Tree) supporting insert, search, and startsWith operations in O(L) time.",
                    "question_type": "Coding"
                }
            ]
        },
        "Searching and Sorting": {
            "Beginner": [
                {
                    "question": "What is the difference between Linear Search and Binary Search in terms of prerequisites and complexity?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain Bubble Sort and why its average and worst-case time complexity is O(N^2).",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is a stable sorting algorithm? Name one stable and one unstable sorting algorithm.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Write code for iterative Binary Search on a sorted array.",
                    "question_type": "Coding"
                },
                {
                    "question": "How does Selection Sort work and what is its time complexity?",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "Explain Merge Sort: why is it divide-and-conquer, and what are its time and auxiliary space complexities?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain QuickSort: how does partitioning work, and why can its worst-case complexity degrade to O(N^2)?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How does Binary Search apply to search in a Rotated Sorted Array?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is HeapSort and how does it achieve in-place sorting in O(N log N) worst-case time?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain the Binary Search on Answer pattern with an example like book allocation or aggressive cows.",
                    "question_type": "Scenario-based"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain Timsort: why is it used as the default sorting algorithm in Python and Java?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does Quickselect find the Kth smallest element in an unsorted array in O(N) average time?",
                    "question_type": "Coding"
                },
                {
                    "question": "Analyze non-comparison-based sorting algorithms: Counting Sort, Radix Sort, and Bucket Sort.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Prove why comparison-based sorting algorithms have a theoretical lower bound of Omega(N log N).",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain median-of-medians algorithm for guaranteed O(N) worst-case pivot selection in Quickselect.",
                    "question_type": "Conceptual"
                }
            ]
        },
        "Hashing": {
            "Beginner": [
                {
                    "question": "What is a Hash Function and what properties define a good hash function?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is a hash collision and why can collisions never be completely eliminated?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the average time complexity of insertion, deletion, and search in a Hash Table?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between Separate Chaining and Open Addressing for collision resolution?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Write code to find the first non-repeating character in a string using a frequency hash map.",
                    "question_type": "Coding"
                }
            ],
            "Intermediate": [
                {
                    "question": "Explain Linear Probing, Quadratic Probing, and Double Hashing in open addressing.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the Load Factor in a hash table and how does rehashing work when the threshold is exceeded?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How do you solve the Longest Substring Without Repeating Characters problem using hashing in O(N) time?",
                    "question_type": "Coding"
                },
                {
                    "question": "How do you find the count of subarrays with a given sum K in O(N) time using prefix sum and hashing?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What are the vulnerabilities of predictable hash functions against Hash Denial of Service (HashDoS) attacks?",
                    "question_type": "Scenario-based"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain Consistent Hashing and its vital role in distributed caches (like Memcached) and Dynamo-style databases.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is a Bloom Filter? How does it provide probabilistic set membership with zero false negatives?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain Cuckoo Hashing and how it achieves guaranteed O(1) worst-case lookup time.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does Rabin-Karp string matching algorithm use rolling hash technique in O(N+M) time?",
                    "question_type": "Coding"
                },
                {
                    "question": "Analyze Count-Min Sketch and HyperLogLog data structures for massive stream frequency and cardinality estimation.",
                    "question_type": "Conceptual"
                }
            ]
        },
        "Dynamic Programming": {
            "Beginner": [
                {
                    "question": "What is Dynamic Programming and what two fundamental properties must a problem have to be solved with DP?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between Top-Down (Memoization) and Bottom-Up (Tabulation) DP?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Write the memoized and tabulated solutions to calculate the Nth Fibonacci number.",
                    "question_type": "Coding"
                },
                {
                    "question": "Explain the Climbing Stairs problem and its recurrence relation.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Why does pure recursion on overlapping subproblems lead to exponential O(2^N) time complexity?",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "Explain the 0/1 Knapsack problem: define the state DP[i][w] and formulate its state transition equation.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How do you solve the Longest Common Subsequence (LCS) problem in O(N*M) time and print the resulting string?",
                    "question_type": "Coding"
                },
                {
                    "question": "Solve the Coin Change problem (minimum coins needed to make amount V) using 1D array space optimization.",
                    "question_type": "Coding"
                },
                {
                    "question": "Explain the Longest Increasing Subsequence (LIS) problem and its O(N log N) solution using patience sorting / binary search.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How do you solve the House Robber problem using DP with O(1) auxiliary space?",
                    "question_type": "Problem-solving"
                }
            ],
            "Advanced": [
                {
                    "question": "Solve the Edit Distance (Levenshtein Distance) problem between two strings using dynamic programming.",
                    "question_type": "Coding"
                },
                {
                    "question": "Explain Matrix Chain Multiplication (MCM) pattern and its O(N^3) interval DP formulation.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How does Bitmask DP solve the Traveling Salesperson Problem (TSP) in O(N^2 * 2^N) time?",
                    "question_type": "Coding"
                },
                {
                    "question": "Explain Digit DP for counting numbers with specific digit properties in a range [A, B].",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Solve the Word Break II problem using DP combined with backtracking / memoization.",
                    "question_type": "Problem-solving"
                }
            ]
        },
        "Time and Space Complexity": {
            "Beginner": [
                {
                    "question": "What is Big-O notation, and why is it used to describe algorithm performance?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Arrange these complexities in increasing order: O(N log N), O(1), O(N^2), O(N), O(2^N), O(log N).",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between Time Complexity and Space Complexity?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the time complexity of searching an element in an unsorted array vs a sorted array?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What does O(1) space complexity mean?",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "What is Amortized Analysis? Explain why dynamic array resizing has amortized O(1) insertion time.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain the Master Theorem for solving divide-and-conquer recurrences: T(N) = aT(N/b) + f(N).",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is Auxiliary Space vs Total Space Complexity in recursive algorithms?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Analyze the time and space complexity of DFS on a graph with V vertices and E edges.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Why do recursive Fibonacci algorithms consume O(N) call-stack space despite having no arrays allocated?",
                    "question_type": "Conceptual"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain Akra-Bazzi method and when it must be used instead of the standard Master Theorem.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are NP-Complete and NP-Hard problems? How is polynomial reduction used in complexity proofs?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Analyze the cache complexity and memory bus bandwidth limitations of external sorting for multi-terabyte datasets.",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Explain the Potential Method of amortized analysis with an example like splay trees or binary counters.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is space-time tradeoff? Give a real-world system architecture example where space was traded for time.",
                    "question_type": "Scenario-based"
                }
            ]
        }
    },
    "Web Development": {
        "HTML": {
            "Beginner": [
                {
                    "question": "What is semantic HTML and why is it important for SEO and accessibility (a11y)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between block-level elements and inline elements in HTML?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the purpose of the `<!DOCTYPE html>` declaration?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are HTML attributes (like `alt`, `href`, `src`, `title`) and how do they work?",
                    "question_type": "Practical"
                },
                {
                    "question": "What are `<meta>` tags and why is `<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">` essential?",
                    "question_type": "Practical"
                }
            ],
            "Intermediate": [
                {
                    "question": "What are HTML5 storage options: LocalStorage, SessionStorage, and Cookies? Compare capacity and lifecycle.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do `async` and `defer` attributes on `<script>` tags differ in script fetching and execution?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain the HTML5 Web Worker API and how it enables background multithreading without freezing the main thread.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are ARIA attributes (`role`, `aria-label`, `aria-hidden`) and how do screen readers use them?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is the HTML `<canvas>` element and how does it compare with SVG for graphic rendering?",
                    "question_type": "Conceptual"
                }
            ],
            "Advanced": [
                {
                    "question": "How do Web Components (Custom Elements, Shadow DOM, HTML Templates) enable encapsulated modularity without frameworks?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain resource hints: `preload`, `prefetch`, `preconnect`, and `dns-prefetch` for web performance optimization.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How does the browser parse HTML into the DOM tree and handle spec-mandated error recovery?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain Content Security Policy (CSP) headers and how to mitigate XSS (Cross-Site Scripting) attacks.",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Analyze Progressive Web App (PWA) architecture: Web App Manifest and Service Worker caching strategies.",
                    "question_type": "Problem-solving"
                }
            ]
        },
        "CSS": {
            "Beginner": [
                {
                    "question": "Explain the CSS Box Model: content, padding, border, and margin.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between `box-sizing: content-box` and `box-sizing: border-box`?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does CSS specificity calculate which styles take precedence (inline, ID, class, tag)?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What are the common CSS position properties (`static`, `relative`, `absolute`, `fixed`, `sticky`)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do CSS media queries make websites responsive across mobile and desktop devices?",
                    "question_type": "Practical"
                }
            ],
            "Intermediate": [
                {
                    "question": "Explain CSS Flexbox: compare `justify-content` (main axis) with `align-items` (cross axis).",
                    "question_type": "Practical"
                },
                {
                    "question": "Explain CSS Grid: when should you choose CSS Grid over Flexbox?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "What are CSS Custom Properties (CSS variables) and how do they cascade dynamically in the DOM?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is the difference between relative CSS units: `rem`, `em`, `vh`, `vw`, and `%`?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What causes CSS reflow (layout) vs repaint, and how do transforms and opacity optimize animations?",
                    "question_type": "Problem-solving"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain Block Formatting Context (BFC): what triggers it and how does it prevent margin collapsing?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do hardware-accelerated CSS properties trigger GPU compositing layers?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Discuss CSS architecture methodologies: BEM vs Utility-first (Tailwind CSS) vs CSS Modules vs CSS-in-JS.",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Explain CSS subgrid and container queries introduced in modern CSS standards.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do you optimize Critical CSS to eliminate render-blocking stylesheets and boost Core Web Vitals (FCP, LCP)?",
                    "question_type": "Problem-solving"
                }
            ]
        },
        "JavaScript": {
            "Beginner": [
                {
                    "question": "What are the differences between `var`, `let`, and `const` in JavaScript regarding scope and hoisting?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between `==` and `===` in JavaScript?",
                    "question_type": "Practical"
                },
                {
                    "question": "Explain data types in JavaScript: primitive types vs reference types.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is a callback function in JavaScript and how is it used in event listeners?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is the DOM (Document Object Model) and how do `querySelector()` and `getElementById()` interact with it?",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "Explain the JavaScript Event Loop: Call Stack, Web APIs, Task Queue (Macrotasks), and Microtask Queue.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is a Closure in JavaScript? Provide an example of how closures enable data privacy.",
                    "question_type": "Coding"
                },
                {
                    "question": "Explain Promises in JavaScript and how `async`/`await` syntactic sugar works.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is the difference between regular functions and arrow functions regarding the `this` binding and `arguments` object?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain Event Bubbling and Event Capturing in the DOM, and what `stopPropagation()` does.",
                    "question_type": "Practical"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain Prototype Inheritance in JavaScript and how the `__proto__` prototype chain resolves properties.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does JavaScript memory management and garbage collection (Mark-and-Sweep) work, and how can closures cause leaks?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Implement a custom `debounce` and `throttle` function from scratch in pure JavaScript.",
                    "question_type": "Coding"
                },
                {
                    "question": "What are JavaScript Generators (`function*`) and Iterators, and how do they enable asynchronous streams?",
                    "question_type": "Practical"
                },
                {
                    "question": "Explain V8 engine optimizations: Hidden Classes, Inline Caching, Ignition interpreter, and TurboFan JIT compiler.",
                    "question_type": "Conceptual"
                }
            ]
        },
        "React": {
            "Beginner": [
                {
                    "question": "What is React and what problem does the Virtual DOM solve?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is JSX in React and how is it transformed by Babel?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between `props` and `state` in React?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do you handle click and input events in React components?",
                    "question_type": "Practical"
                },
                {
                    "question": "Why is a `key` prop required when rendering lists of elements in React?",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "Explain the `useEffect` hook: how do the dependency array and cleanup function operate?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is the difference between `useMemo` and `useCallback` in React performance optimization?",
                    "question_type": "Practical"
                },
                {
                    "question": "How does the Context API in React manage global state, and when does it cause unnecessary re-renders?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "What are controlled vs uncontrolled components in React forms with `useRef`?",
                    "question_type": "Practical"
                },
                {
                    "question": "Explain the rules of React Hooks: why can't hooks be called conditionally or inside loops?",
                    "question_type": "Conceptual"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain React Fiber architecture: reconciliation, priority queues, and cooperative time-slicing.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does React 18 Concurrent Mode enable features like `useTransition` and `useDeferredValue`?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How do React Server Components (RSC) differ from traditional Client Components and Server-Side Rendering (SSR)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Implement a custom hook `useFetch` with caching, cancellation via AbortController, and retry logic.",
                    "question_type": "Coding"
                },
                {
                    "question": "Discuss state management tradeoffs in large-scale apps: Redux Toolkit vs Zustand vs TanStack Query (React Query).",
                    "question_type": "Scenario-based"
                }
            ]
        },
        "Node.js": {
            "Beginner": [
                {
                    "question": "What is Node.js and how does it run JavaScript on the server outside the browser?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is npm (Node Package Manager) and what is the difference between `dependencies` and `devDependencies`?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between CommonJS (`require`) and ES Modules (`import/export`) in Node.js?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do you read a file asynchronously in Node.js using the `fs` module?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is the role of `package.json` and `package-lock.json`?",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "Explain the Libuv event loop architecture in Node.js: timers, pending callbacks, poll, check, and close phases.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are Node.js Streams (Readable, Writable, Duplex, Transform) and why are they essential for large payloads?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is `process.nextTick()` and how does its priority differ from `setImmediate()` and `setTimeout()`?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does the Node.js Cluster module allow a single-threaded server to utilize multiple CPU cores?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is middleware in Express.js and how does the `(req, res, next)` pipeline execute?",
                    "question_type": "Practical"
                }
            ],
            "Advanced": [
                {
                    "question": "How do you detect, profile, and fix memory leaks in production Node.js applications using heap snapshots?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is backpressure in Node.js streams and how does `.pipe()` handle buffer flow control?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Compare Worker Threads (`worker_threads`) vs child processes (`child_process.fork`) for CPU-heavy tasks in Node.js.",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "How do you prevent Event Loop blocking attacks in high-throughput API gateways?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Design a graceful shutdown handler in Node.js that stops accepting requests, drains connections, and flushes logs.",
                    "question_type": "Coding"
                }
            ]
        },
        "REST APIs": {
            "Beginner": [
                {
                    "question": "What is a RESTful API and what are the primary HTTP methods (GET, POST, PUT, DELETE, PATCH)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between PUT and PATCH methods?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain common HTTP status code categories: 2xx (Success), 3xx (Redirect), 4xx (Client Error), 5xx (Server Error).",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the purpose of HTTP headers (e.g. `Content-Type`, `Authorization`, `Accept`)?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is JSON and why has it become the universal standard for API data exchange?",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "What is idempotent HTTP method and which methods (GET, PUT, DELETE, POST) are idempotent?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain authentication vs authorization in APIs. How does JWT (JSON Web Token) stateless authentication work?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is CORS (Cross-Origin Resource Sharing) and what is a CORS preflight (`OPTIONS`) request?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "How do pagination patterns (offset-based vs cursor-based) compare for high-volume API feeds?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is API versioning and what are the pros/cons of URI versioning vs Header versioning?",
                    "question_type": "Scenario-based"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain Rate Limiting algorithms in distributed systems: Token Bucket, Leaky Bucket, and Sliding Window Counter.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is HATEOAS (Hypermedia As The Engine Of Application State) and Richardson Maturity Model Level 3?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Compare REST API architectural tradeoffs with GraphQL and gRPC for microservices.",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "How does HTTP caching work with `Cache-Control`, `ETag`, and conditional requests (`If-None-Match`)?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Design an idempotent payment processing API endpoint using idempotency keys and distributed locking.",
                    "question_type": "Coding"
                }
            ]
        },
        "Frontend Development": {
            "Beginner": [
                {
                    "question": "How do HTML, CSS, and JavaScript collaborate to render an interactive web page in a browser?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is responsive web design and mobile-first approach?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are web browser developer tools (DevTools) and how do the Elements and Console tabs assist debugging?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is client-side form validation and why must it always be backed up by server-side validation?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is cross-browser compatibility and why must frontend developers test multiple rendering engines?",
                    "question_type": "Scenario-based"
                }
            ],
            "Intermediate": [
                {
                    "question": "What is the Critical Rendering Path (DOM -> CSSOM -> Render Tree -> Layout -> Paint -> Composite)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain Single Page Application (SPA) vs Multi-Page Application (MPA) in user experience and initial load time.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are Web Vitals: LCP (Largest Contentful Paint), FID/INP (Input Delay), and CLS (Cumulative Layout Shift)?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How does frontend bundling (Webpack, Vite, Rollup) perform code splitting, tree shaking, and minification?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain state management patterns on the frontend and how to prevent state synchronization issues.",
                    "question_type": "Scenario-based"
                }
            ],
            "Advanced": [
                {
                    "question": "How do Server-Side Rendering (SSR), Static Site Generation (SSG), and Incremental Static Regeneration (ISR) differ?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain micro-frontend architectures: Module Federation vs iframe isolation vs Web Components.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How do you protect a frontend application against XSS (Cross-Site Scripting), CSRF, and Clickjacking?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Analyze frontend caching strategies: HTTP Cache headers, Service Worker Cache API, and memory state.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How do you profile runtime performance and JavaScript execution bottlenecks using the Chrome DevTools Performance Profiler?",
                    "question_type": "Practical"
                }
            ]
        },
        "Backend Development": {
            "Beginner": [
                {
                    "question": "What is the role of a backend server and how does it process requests from clients?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is an environment variable (`.env`) and why should API keys and database credentials never be hardcoded?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is the difference between a Web Server (e.g. Nginx, Apache) and an Application Server?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is a database and how does a backend application communicate with it?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is synchronous vs asynchronous execution in backend request handling?",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "Explain Monolithic vs Microservices architecture: pros, cons, and operational complexity.",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "What is an ORM (Object-Relational Mapping)? What is the N+1 query problem and how do you resolve it?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How does server-side caching with Redis or Memcached reduce database load?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is a message broker (RabbitMQ, Apache Kafka) and how does it enable asynchronous event-driven architectures?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain the role of an API Gateway and Reverse Proxy in routing, SSL termination, and load balancing.",
                    "question_type": "Conceptual"
                }
            ],
            "Advanced": [
                {
                    "question": "How do you implement distributed transactions across microservices using the Saga pattern (Choreography vs Orchestration)?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain database sharding vs read replicas and how to handle master failover with zero data loss.",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "What is the Circuit Breaker pattern and how does it prevent cascading service failures under high latency?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Describe OAuth 2.0 and OpenID Connect authorization code grant flow with PKCE.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Design a high-scale real-time notification service handling millions of concurrent WebSocket connections.",
                    "question_type": "Coding"
                }
            ]
        }
    },
    "Database Management Systems (DBMS)": {
        "DBMS Fundamentals": {
            "Beginner": [
                {
                    "question": "What is a DBMS and what advantages does it offer over traditional file-based storage systems?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are the three levels of Data Abstraction in DBMS (Physical, Logical, View levels)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between Data Definition Language (DDL) and Data Manipulation Language (DML)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is a primary key, foreign key, and candidate key in database design?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is data redundancy and why does it cause update and deletion anomalies?",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "What is the difference between logical data independence and physical data independence?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain Entity-Relationship (ER) modeling: entities, attributes, relationships, and cardinality ratios.",
                    "question_type": "Practical"
                },
                {
                    "question": "What is a Database View and what is the difference between a standard view and a materialized view?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is a Database Trigger and stored procedure? When should business logic be placed in the database vs application layer?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Explain the difference between clustered and non-clustered indexes in database tables.",
                    "question_type": "Conceptual"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain the CAP theorem (Consistency, Availability, Partition Tolerance) and PACELC theorem in distributed databases.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do Write-Ahead Logging (WAL) and ARIES recovery algorithms guarantee Durability across power failures?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Analyze query planner optimization: cost-based optimization vs rule-based optimization.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain Multi-Version Concurrency Control (MVCC) and how it enables non-blocking snapshot reads in PostgreSQL and MySQL.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Design a data retention and partitioning strategy for an enterprise database handling 100 million rows per day.",
                    "question_type": "Scenario-based"
                }
            ]
        },
        "Relational Database Concepts": {
            "Beginner": [
                {
                    "question": "What is a relational database and how is data structured in tuples and relations?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is referential integrity and how do foreign key constraints enforce it?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are cascading actions (`ON DELETE CASCADE`, `ON UPDATE CASCADE`) in relational foreign keys?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is a composite key and when is it appropriate to use one?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between NULL and zero or an empty string in relational databases?",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "Explain Relational Algebra fundamental operations: Selection, Projection, Cartesian Product, Union, and Set Difference.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are surrogate keys vs natural keys? Discuss trade-offs in database schema design.",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "What is schema evolution and how do migration tools manage schema changes in production databases without downtime?",
                    "question_type": "Practical"
                },
                {
                    "question": "Explain self-referencing relationships (hierarchical relations like Employee-Manager) in a single table.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is domain integrity and how do check constraints enforce specific column validation?",
                    "question_type": "Practical"
                }
            ],
            "Advanced": [
                {
                    "question": "How does relational division operator in relational algebra solve queries like 'find students enrolled in all courses'?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Analyze distributed foreign key validation challenges in sharded relational databases (e.g. Citus, Vitess).",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Explain how relational engines compile declarative SQL queries into physical relational algebra operator trees.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Compare relational database engines (PostgreSQL vs MySQL InnoDB) regarding locking granularity and MVCC implementations.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Design an audit logging schema using temporal tables / historical versioning triggers with minimal storage overhead.",
                    "question_type": "Coding"
                }
            ]
        },
        "Normalization": {
            "Beginner": [
                {
                    "question": "What is Database Normalization and what is its primary objective?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are Insertion, Deletion, and Update Anomalies? Give an example of each.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are the rules and requirements for First Normal Form (1NF)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is Functional Dependency and how is it represented ($X \\rightarrow Y$)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is Second Normal Form (2NF) and what is partial dependency?",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "What is Third Normal Form (3NF) and what is transitive dependency?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is Boyce-Codd Normal Form (BCNF) and how is it stricter than 3NF?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Given a relation $R(A, B, C, D)$ with FDs $A \\rightarrow B$, $B \\rightarrow C$, find the candidate key and normalize to 3NF.",
                    "question_type": "Coding"
                },
                {
                    "question": "What is Denormalization and when is it intentionally applied in read-heavy production databases?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "What is lossy vs lossless join decomposition and why must all normalizations be lossless?",
                    "question_type": "Problem-solving"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain Fourth Normal Form (4NF) and Multi-Valued Dependencies (MVD).",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is Fifth Normal Form (5NF / Project-Join Normal Form) and Join Dependency?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does Dependency Preservation testing verify that all FDs are enforceable within individual decomposed tables?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Analyze Armstrong\\'s Axioms (Reflexivity, Augmentation, Transitivity) and attribute closure calculation algorithm.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Design a dimensional star schema vs snowflake schema in data warehousing: discuss denormalization trade-offs.",
                    "question_type": "Scenario-based"
                }
            ]
        },
        "Transactions": {
            "Beginner": [
                {
                    "question": "What is a database transaction and what does it represent?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are the states of a transaction (Active, Partially Committed, Committed, Failed, Aborted)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What do `COMMIT` and `ROLLBACK` commands do in a database transaction?",
                    "question_type": "Practical"
                },
                {
                    "question": "Why is banking transfer the classic example of a database transaction requiring all-or-nothing execution?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "What is an autocommit mode in database connections?",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "What is a serial schedule vs a non-serial concurrent schedule?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is Conflict Serializability and how do Precedence Graphs (Serialization Graphs) detect cycle conflicts?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is View Serializability and how does it compare to Conflict Serializability?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are recoverable schedules and cascade-less schedules in concurrent transaction execution?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain Deadlock detection (Wait-For Graph) and Deadlock prevention (Wait-Die vs Wound-Wait schemes).",
                    "question_type": "Problem-solving"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain Two-Phase Locking (2PL) protocol: Growing phase, Shrinking phase, and Strict 2PL / Rigorous 2PL.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does Timestamp-Ordering protocol ensure serializability without locks?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain Two-Phase Commit (2PC) protocol in distributed transactions: Prepare phase, Commit phase, and coordinator failure recovery.",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "What is Write Skew anomaly and how does Snapshot Isolation fail to prevent it without Serializable isolation?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain the Raft consensus algorithm and its role in distributed transactional log replication (like CockroachDB).",
                    "question_type": "Conceptual"
                }
            ]
        },
        "Indexing": {
            "Beginner": [
                {
                    "question": "What is a database index and why is it used?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the tradeoff of adding indexes to a database table regarding SELECT vs INSERT/UPDATE/DELETE performance?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between a Clustered Index and a Non-Clustered (Secondary) Index?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Can a database table have more than one Clustered Index? Why or why not?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is a unique index and how does it differ from a primary key constraint?",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "Why are B-Trees and B+ Trees the standard data structure for database indexes instead of Binary Search Trees?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between B-Trees and B+ Trees in leaf node storage and sequential range scans?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is a Composite (Multi-Column) Index and how does the Leftmost Prefix Rule dictate its usage?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is a Covering Index and how does an index-only scan eliminate table row lookups?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is Index Cardinality and how does low cardinality (e.g. Gender, Boolean) impact index efficiency?",
                    "question_type": "Scenario-based"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain Log-Structured Merge-Trees (LSM-Trees) and why write-heavy databases (Cassandra, RocksDB) prefer LSM over B-Trees.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are Specialized Indexes: Bitmap Indexes, Hash Indexes, GIN/GiST (Inverted Indexes in Postgres) and their use cases?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How do database engines handle index fragmentation and when should `REINDEX` or `ALTER INDEX ... REBUILD` be scheduled?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "How do B+ tree page splits and merges operate during high-concurrency concurrent write workloads?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Analyze an `EXPLAIN ANALYZE` execution plan to diagnose why an index is ignored in favor of a Sequential Scan.",
                    "question_type": "Coding"
                }
            ]
        },
        "Joins": {
            "Beginner": [
                {
                    "question": "What is an INNER JOIN and what records does it return?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between a LEFT OUTER JOIN, RIGHT OUTER JOIN, and FULL OUTER JOIN?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is a CROSS JOIN (Cartesian Product) and what is the formula for the number of rows produced?",
                    "question_type": "Practical"
                },
                {
                    "question": "Write a query joining an `employees` table with a `departments` table on `department_id`.",
                    "question_type": "Coding"
                },
                {
                    "question": "What is a Self Join and when would you use it?",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "Explain the three physical join algorithms used by database query engines: Nested Loop Join, Hash Join, and Sort-Merge Join.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "When does the query optimizer choose a Hash Join over a Nested Loop Join?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is the difference between the `ON` clause condition and the `WHERE` clause condition in outer joins?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is a Natural Join and why is it considered risky in production schemas?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do you find records in Table A that have no matching records in Table B using an anti-join pattern?",
                    "question_type": "Coding"
                }
            ],
            "Advanced": [
                {
                    "question": "Analyze memory allocation and temp spillover behavior when Hash Joins exceed database work memory (`work_mem`).",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How do Distributed Joins work in sharded databases (Broadcast Join vs Hash Partitioned Shuffle Join)?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Explain Semi-Join and Anti-Join optimizations performed by relational query rewrite engines.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Optimize a complex query with 5+ joins that is experiencing performance degradation due to suboptimal join order selection.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain lateral joins (`CROSS JOIN LATERAL` in PostgreSQL / `CROSS APPLY` in SQL Server) and their use cases.",
                    "question_type": "Coding"
                }
            ]
        },
        "ACID Properties": {
            "Beginner": [
                {
                    "question": "What does the ACID acronym stand for in database management?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain Atomicity with a real-world example: what does 'all or nothing' mean?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is Consistency in ACID properties?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is Isolation in ACID properties and why is it necessary in multi-user systems?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is Durability and how does a database guarantee data is not lost after a successful transaction commit?",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "Explain the four ANSI SQL Transaction Isolation Levels: Read Uncommitted, Read Committed, Repeatable Read, and Serializable.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are concurrency read phenomena: Dirty Reads, Non-Repeatable Reads, and Phantom Reads?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Which concurrency phenomena does each SQL isolation level prevent?",
                    "question_type": "Practical"
                },
                {
                    "question": "How does the Write-Ahead Log (WAL) ensure both Atomicity (via UNDO log) and Durability (via REDO log)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the performance trade-off between higher isolation levels (like Serializable) and transaction throughput?",
                    "question_type": "Scenario-based"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain Serializable Snapshot Isolation (SSI) in PostgreSQL and how it detects Serialization Failures using rw-antidependency graphs.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How does Spanner (Google Spanner) achieve external consistency (Strict Serializability) globally using TrueTime API and GPS clocks?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Compare Pessimistic Concurrency Control (locks) vs Optimistic Concurrency Control (OCC / version checking) under high contention.",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Analyze fsync latency, write-combining buffers, and disk controller volatile cache hazards in achieving true Durability.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How does eventual consistency in BASE systems compare to strict ACID consistency in financial systems?",
                    "question_type": "Conceptual"
                }
            ]
        }
    },
    "SQL": {
        "SQL Basics": {
            "Beginner": [
                {
                    "question": "What is SQL and what are its standard sub-languages (DDL, DML, DCL, TCL)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What do `CREATE TABLE`, `ALTER TABLE`, and `DROP TABLE` statements do?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is the difference between `DELETE`, `TRUNCATE`, and `DROP` commands?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do you insert a new record into a database table using the `INSERT INTO` statement?",
                    "question_type": "Coding"
                },
                {
                    "question": "How do you update existing records in a table using `UPDATE ... SET ... WHERE`?",
                    "question_type": "Coding"
                }
            ],
            "Intermediate": [
                {
                    "question": "What is the logical query processing order of SQL clauses (FROM -> WHERE -> GROUP BY -> HAVING -> SELECT -> ORDER BY -> LIMIT)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Why can\\'t you use column aliases defined in the `SELECT` clause inside the `WHERE` clause?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is the difference between `DISTINCT` and `GROUP BY` when eliminating duplicate rows?",
                    "question_type": "Practical"
                },
                {
                    "question": "Explain how `NULL` comparisons work in SQL: why must you use `IS NULL` instead of `= NULL`?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does the `COALESCE()` and `NULLIF()` function work in SQL data transformations?",
                    "question_type": "Coding"
                }
            ],
            "Advanced": [
                {
                    "question": "How do you perform recursive queries in SQL using Common Table Expressions (`WITH RECURSIVE`) to traverse hierarchies?",
                    "question_type": "Coding"
                },
                {
                    "question": "Explain SQL injection vulnerabilities and how parameterized queries prevent them at the protocol level.",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "How does SQL Server / Oracle / PostgreSQL handle table partitions (Range, List, Hash) at the SQL syntax level?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are User-Defined Functions (UDFs) and what are their performance impacts on query parallelism?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Write an upsert statement (`INSERT ... ON CONFLICT DO UPDATE` or `MERGE INTO`) to synchronize tables.",
                    "question_type": "Coding"
                }
            ]
        },
        "SELECT Queries": {
            "Beginner": [
                {
                    "question": "Write a query to select all columns and rows from an `employees` table.",
                    "question_type": "Coding"
                },
                {
                    "question": "How do you filter records using the `WHERE` clause with comparison operators (`>`, `<`, `=`, `!=`)?",
                    "question_type": "Coding"
                },
                {
                    "question": "How do `AND`, `OR`, and `NOT` logical operators work in SQL `WHERE` clauses?",
                    "question_type": "Practical"
                },
                {
                    "question": "How do you sort results using `ORDER BY` in ascending (`ASC`) and descending (`DESC`) order?",
                    "question_type": "Coding"
                },
                {
                    "question": "How do you restrict the number of rows returned using `LIMIT` or `TOP`?",
                    "question_type": "Practical"
                }
            ],
            "Intermediate": [
                {
                    "question": "How does the `LIKE` operator work with wildcards `%` and `_` for pattern matching?",
                    "question_type": "Practical"
                },
                {
                    "question": "How do `BETWEEN` and `IN` operators simplify filtering in `WHERE` clauses?",
                    "question_type": "Coding"
                },
                {
                    "question": "Write a query using `CASE WHEN ... THEN ... ELSE ... END` conditional logic in a `SELECT` projection.",
                    "question_type": "Coding"
                },
                {
                    "question": "How do you handle sorting when values contain `NULL` (`NULLS FIRST` vs `NULLS LAST`)?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Write a query to find all employees whose names start with 'A' and contain at least 5 letters.",
                    "question_type": "Coding"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain Window Functions: how do `ROW_NUMBER()`, `RANK()`, and `DENSE_RANK()` differ?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Write a query to find the Nth highest salary in an `employees` table using window functions.",
                    "question_type": "Coding"
                },
                {
                    "question": "How do `LEAD()` and `LAG()` analytical window functions access previous and subsequent rows without self-joins?",
                    "question_type": "Coding"
                },
                {
                    "question": "Explain frame specification in window functions (`ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING` vs `RANGE`).",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Write a query to compute a 7-day rolling average of daily sales using window functions.",
                    "question_type": "Coding"
                }
            ]
        },
        "Joins": {
            "Beginner": [
                {
                    "question": "What is the difference between an `INNER JOIN` and a `LEFT JOIN`?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Write an SQL query to retrieve employee names along with their respective department names using `INNER JOIN`.",
                    "question_type": "Coding"
                },
                {
                    "question": "What will happen if you omit the `ON` clause in an SQL join statement?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do you join three tables (`Customers`, `Orders`, `Products`) in a single query?",
                    "question_type": "Coding"
                },
                {
                    "question": "What is a `FULL OUTER JOIN` and which databases support it natively?",
                    "question_type": "Practical"
                }
            ],
            "Intermediate": [
                {
                    "question": "How do you perform a Self Join to list employees alongside their managers from a single `Employees` table?",
                    "question_type": "Coding"
                },
                {
                    "question": "Write a query using a `LEFT JOIN` to find all customers who have never placed an order.",
                    "question_type": "Coding"
                },
                {
                    "question": "What is the difference between filtering conditions inside the `ON` clause vs inside the `WHERE` clause in a `LEFT JOIN`?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain the Cartesian Product created by a `CROSS JOIN` and a practical scenario where it is required.",
                    "question_type": "Practical"
                },
                {
                    "question": "What is a `NATURAL JOIN` and why do enterprise SQL coding guidelines forbid it?",
                    "question_type": "Scenario-based"
                }
            ],
            "Advanced": [
                {
                    "question": "How do you write a query using `CROSS JOIN LATERAL` (or `CROSS APPLY`) to calculate top 3 transactions per customer?",
                    "question_type": "Coding"
                },
                {
                    "question": "Analyze the execution plan differences between an `EXISTS` subquery vs an `INNER JOIN` with `DISTINCT`.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Write an optimal query to reconcile discrepancies between two financial balance tables using full outer join.",
                    "question_type": "Coding"
                },
                {
                    "question": "How does query reordering by cost-based optimizers handle multi-table join trees (Left-deep vs Bushy trees)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do non-equi joins (joins with `>`, `<`, or `BETWEEN`) execute and why can't they use hash join algorithms?",
                    "question_type": "Problem-solving"
                }
            ]
        },
        "Subqueries": {
            "Beginner": [
                {
                    "question": "What is a subquery in SQL and where can it be placed (SELECT, FROM, WHERE clauses)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is a Single-row subquery vs a Multiple-row subquery?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What operators (`IN`, `ANY`, `ALL`, `EXISTS`) are used with multiple-row subqueries?",
                    "question_type": "Practical"
                },
                {
                    "question": "Write a query to find all employees earning more than the company average salary using a subquery.",
                    "question_type": "Coding"
                },
                {
                    "question": "What is the difference between a subquery in the `FROM` clause (derived table) and a Common Table Expression (CTE)?",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "What is a Correlated Subquery and why does it execute once for every row processed by the outer query?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain the difference between `EXISTS` and `IN` operators and their performance characteristics with NULL values.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Write a query using a correlated subquery to find employees who earn more than the average salary of their specific department.",
                    "question_type": "Coding"
                },
                {
                    "question": "What is the `NOT EXISTS` vs `NOT IN` trap when the subquery returns even a single `NULL` value?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "How do Common Table Expressions (`WITH cte AS (...)`) improve query readability and modularity over nested subqueries?",
                    "question_type": "Practical"
                }
            ],
            "Advanced": [
                {
                    "question": "How does the query optimizer unnest subqueries into semi-joins or anti-joins for performance acceleration?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Write a recursive CTE to generate a calendar date dimension table for the entire year 2026.",
                    "question_type": "Coding"
                },
                {
                    "question": "Write a recursive CTE to calculate the total hierarchy path and organizational level of employees under a CEO.",
                    "question_type": "Coding"
                },
                {
                    "question": "Analyze scalar subquery caching mechanisms inside database execution engines.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Rewrite a correlated subquery with heavy execution cost into an efficient window function or joined derived table.",
                    "question_type": "Problem-solving"
                }
            ]
        },
        "Aggregate Functions": {
            "Beginner": [
                {
                    "question": "What are aggregate functions in SQL? Name five commonly used aggregate functions (`COUNT`, `SUM`, `AVG`, `MIN`, `MAX`).",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between `COUNT(*)` and `COUNT(column_name)` in SQL?",
                    "question_type": "Practical"
                },
                {
                    "question": "How do aggregate functions handle `NULL` values when computing sums or averages?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Write a query to find the total and average revenue from an `orders` table.",
                    "question_type": "Coding"
                },
                {
                    "question": "Can you use an aggregate function directly in a `WHERE` clause? Why or why not?",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "How does `COUNT(DISTINCT column_name)` compute unique occurrences?",
                    "question_type": "Practical"
                },
                {
                    "question": "Write a query to calculate the median salary in an `employees` table without built-in median functions.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain string aggregation functions like `STRING_AGG()` (Postgres/SQL Server) or `GROUP_CONCAT()` (MySQL).",
                    "question_type": "Practical"
                },
                {
                    "question": "How do you compute weighted averages in SQL using `SUM(value * weight) / SUM(weight)`?",
                    "question_type": "Coding"
                },
                {
                    "question": "What is the difference between standard aggregate functions and windowed aggregate functions (`SUM() OVER (...)`)?",
                    "question_type": "Conceptual"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain user-defined aggregate functions (UDAFs) and their state transition functions.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do approximate aggregate functions (like `APPROX_COUNT_DISTINCT` using HyperLogLog) scale in big data SQL engines?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Analyze query performance and parallel aggregation (Partial Aggregate -> Final Aggregate) across multiple CPU workers.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Write an SQL query to calculate percentage distribution of sales by category against grand total in a single pass.",
                    "question_type": "Coding"
                },
                {
                    "question": "How do statistical aggregate functions (`STDDEV`, `VARIANCE`, `CORR`) function inside analytical data warehouses?",
                    "question_type": "Conceptual"
                }
            ]
        },
        "Group By and Having": {
            "Beginner": [
                {
                    "question": "What is the purpose of the `GROUP BY` clause in SQL?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between the `WHERE` clause and the `HAVING` clause?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Why must any column in the `SELECT` list that is not in an aggregate function appear in the `GROUP BY` clause?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Write a query to find the number of employees in each department.",
                    "question_type": "Coding"
                },
                {
                    "question": "Write a query to find all departments that have more than 5 employees using `HAVING`.",
                    "question_type": "Coding"
                }
            ],
            "Intermediate": [
                {
                    "question": "Explain `GROUPING SETS`, `ROLLUP`, and `CUBE` extensions in SQL for multi-dimensional subtotal reporting.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Write a query using `ROLLUP` to generate total sales by Country, State, and City along with hierarchical subtotals.",
                    "question_type": "Coding"
                },
                {
                    "question": "What is the `GROUPING()` function and how does it distinguish NULL values in raw data from subtotal aggregation NULLs?",
                    "question_type": "Practical"
                },
                {
                    "question": "Can you use multiple conditions and boolean logic (`AND`, `OR`) in a `HAVING` clause?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is the execution order of `GROUP BY` relative to `WHERE` and `HAVING`?",
                    "question_type": "Conceptual"
                }
            ],
            "Advanced": [
                {
                    "question": "How does the query optimizer choose between Stream Aggregate (Sort + Group) vs Hash Aggregate?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Write an optimized query to find duplicate records across 4 composite columns using `GROUP BY` and `HAVING`.",
                    "question_type": "Coding"
                },
                {
                    "question": "Analyze memory pressure and disk spilling when a high-cardinality `GROUP BY` exceeds allocated hash memory.",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Explain filter pushdown: when can conditions in `HAVING` be rewritten by the optimizer into `WHERE` clauses?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Design an SQL pipeline that aggregates billions of time-series records into 5-minute bucket summaries.",
                    "question_type": "Problem-solving"
                }
            ]
        },
        "Constraints": {
            "Beginner": [
                {
                    "question": "What are SQL constraints and why are they used in relational tables?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain `PRIMARY KEY`, `UNIQUE`, `NOT NULL`, and `DEFAULT` constraints.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is a `CHECK` constraint in SQL? Write an example enforcing positive salary.",
                    "question_type": "Coding"
                },
                {
                    "question": "What is a `FOREIGN KEY` constraint and what does it enforce?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do you drop or disable a constraint on an existing table?",
                    "question_type": "Practical"
                }
            ],
            "Intermediate": [
                {
                    "question": "What is the difference between a table-level constraint and a column-level constraint?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are deferrable constraints (`DEFERRABLE INITIALLY DEFERRED`) and why are they vital for circular foreign keys?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What are cascading referential constraints (`ON DELETE SET NULL`, `ON DELETE CASCADE`, `ON DELETE RESTRICT`)?",
                    "question_type": "Practical"
                },
                {
                    "question": "Can a `UNIQUE` constraint accept `NULL` values? How do different database engines (PostgreSQL, SQL Server, MySQL) handle multiple NULLs in unique columns?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How do you add a foreign key constraint to a table that already contains millions of rows without locking the table?",
                    "question_type": "Scenario-based"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain Exclusion Constraints in PostgreSQL (`EXCLUDE USING gist`) and how they prevent overlapping date ranges.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How do constraint validations impact bulk data loading throughput (`BULK INSERT` / `COPY`)?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "How do database query optimizers use check constraints for Partition Pruning (Constraint Exclusion)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Design a relational constraint schema enforcing business rules like 'an employee can only manage one department at a time'.",
                    "question_type": "Coding"
                },
                {
                    "question": "Analyze performance degradation of unindexed foreign key columns during parent table DELETE operations.",
                    "question_type": "Problem-solving"
                }
            ]
        },
        "Views": {
            "Beginner": [
                {
                    "question": "What is an SQL View and why is it often called a 'virtual table'?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do you create and query a view using `CREATE VIEW view_name AS SELECT ...`?",
                    "question_type": "Coding"
                },
                {
                    "question": "What are the security benefits of using views to restrict user access to sensitive columns?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Does a standard SQL view store data physically on disk?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do you modify or drop an existing view in SQL?",
                    "question_type": "Practical"
                }
            ],
            "Intermediate": [
                {
                    "question": "What is an Updatable View? What conditions must a view meet to allow `INSERT`, `UPDATE`, or `DELETE` operations?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the `WITH CHECK OPTION` clause on views and how does it prevent updates that violate view criteria?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is a Materialized View and how does it differ from a standard View in storage and performance?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do you refresh a Materialized View (`REFRESH MATERIALIZED VIEW`) and what is the difference between complete vs incremental refresh?",
                    "question_type": "Practical"
                },
                {
                    "question": "What are the drawbacks and maintenance overheads of deeply nested views (views querying views)?",
                    "question_type": "Scenario-based"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain View Inlining / View Flattening performed by relational query optimizers.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does Query Rewrite work with Materialized Views: when can the optimizer redirect table queries to a precomputed materialized view automatically?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain `INSTEAD OF` triggers on views to enable custom DML mutations on complex multi-table views.",
                    "question_type": "Coding"
                },
                {
                    "question": "Design an incremental refresh architecture for materialized views using write-ahead change data capture (CDC).",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Analyze cache invalidation and replication lag considerations for materialized views in high-traffic reporting dashboards.",
                    "question_type": "Scenario-based"
                }
            ]
        }
    },
    "Operating Systems": {
        "Process Management": {
            "Beginner": [
                {
                    "question": "What is a Process in an Operating System and how does it differ from a Program stored on disk?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain the Process Control Block (PCB) and what essential information it contains.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are the states in the 5-state Process Lifecycle Model (New, Ready, Running, Waiting/Blocked, Terminated)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between a process and a thread?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is a Zombie Process and what is an Orphan Process in Unix/Linux?",
                    "question_type": "Practical"
                }
            ],
            "Intermediate": [
                {
                    "question": "Explain how the `fork()` and `exec()` system calls work together to spawn and replace processes in Unix.",
                    "question_type": "Practical"
                },
                {
                    "question": "What is a Context Switch? What steps does the OS perform during a context switch and what is its performance overhead?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What are Inter-Process Communication (IPC) mechanisms: Pipes, Named Pipes (FIFOs), Message Queues, Shared Memory, and Sockets?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the Critical Section Problem and what three conditions must any valid solution satisfy (Mutual Exclusion, Progress, Bounded Waiting)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain Semaphores (Binary vs Counting) and how `wait()` (P) and `signal()` (V) operations control access.",
                    "question_type": "Coding"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain Peterson\\'s Algorithm and why hardware atomic instructions (`test_and_set`, `compare_and_swap`) are required on modern multi-core CPUs.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What are Linux Copy-On-Write (COW) semantics during `fork()` and how do page table write protections enable memory sharing?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do Unix signals (`SIGKILL`, `SIGTERM`, `SIGSEGV`, `SIGCHLD`) propagate and how are signal handlers executed in user space?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain the Priority Inversion problem in real-time operating systems and how Priority Inheritance protocol resolves it.",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Analyze Linux cgroups (Control Groups) and namespaces: how do they form the foundational container isolation for Docker and Kubernetes?",
                    "question_type": "Conceptual"
                }
            ]
        },
        "Threads": {
            "Beginner": [
                {
                    "question": "What is a Thread and why is it referred to as a lightweight process (LWP)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What resources do threads within the same process share, and what does each thread maintain privately?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are the advantages of multithreading over multiprocessing?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is User-Level Thread (ULT) vs Kernel-Level Thread (KLT)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is a Race Condition and how can it occur when two threads access shared data simultaneously?",
                    "question_type": "Practical"
                }
            ],
            "Intermediate": [
                {
                    "question": "Explain Multithreading Models: Many-to-One, One-to-One, and Many-to-Many.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is a Mutex (Mutual Exclusion lock) and how does it differ from a Binary Semaphore?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is a Spinlock and when is spinning on a lock preferred over blocking/sleeping a thread?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is Thread-Local Storage (TLS) and why is it used?",
                    "question_type": "Practical"
                },
                {
                    "question": "What are Reentrant functions and what makes a function thread-safe?",
                    "question_type": "Conceptual"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain Lock-Free and Wait-Free data structures: how are atomic CAS loops used without locks?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is the ABA Problem in lock-free concurrency and how do tagged pointers (versioned pointers) resolve it?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Analyze CPU cache coherence protocols (MESI / MOESI) and False Sharing across CPU L1/L2 caches in multi-threaded programs.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does Linux NPTL (Native POSIX Thread Library) map threads to kernel tasks via the `clone()` system call?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Design a high-performance thread pool in C/C++ with task work-stealing queues.",
                    "question_type": "Coding"
                }
            ]
        },
        "CPU Scheduling": {
            "Beginner": [
                {
                    "question": "What is CPU Scheduling and what is the difference between preemptive and non-preemptive scheduling?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are the common CPU scheduling criteria: CPU Utilization, Throughput, Turnaround Time, Waiting Time, and Response Time?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain First-Come, First-Served (FCFS) scheduling and the Convoy Effect.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain Shortest Job First (SJF) scheduling and why it is provably optimal for minimizing average waiting time.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does Round Robin (RR) scheduling work and what is the role of the Time Quantum?",
                    "question_type": "Practical"
                }
            ],
            "Intermediate": [
                {
                    "question": "How does the choice of Time Quantum in Round Robin scheduling affect context switch overhead vs system responsiveness?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain Priority Scheduling and how Starvation (indefinite blocking) is mitigated using Aging.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain Multi-Level Queue (MLQ) and Multi-Level Feedback Queue (MLFQ) scheduling.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is Shortest Remaining Time First (SRTF) and how does it handle incoming shorter processes?",
                    "question_type": "Coding"
                },
                {
                    "question": "Given 3 processes with arrival times and burst times, calculate average turnaround and waiting time under Round Robin.",
                    "question_type": "Problem-solving"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain the Linux Completely Fair Scheduler (CFS): virtual runtime (`vruntime`), red-black trees, and latency targets.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is Asymmetric Multiprocessing (AMP) vs Symmetric Multiprocessing (SMP) and NUMA-aware scheduling?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain Hard Real-Time vs Soft Real-Time scheduling: Rate Monotonic Scheduling (RMS) vs Earliest Deadline First (EDF).",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How do CPU affinity (processor binding) and thread migration balance cache warmness vs core load balancing?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Analyze energy-aware scheduling algorithms (EAS) in mobile OS architectures (ARM big.LITTLE / DynamIQ).",
                    "question_type": "Conceptual"
                }
            ]
        },
        "Deadlocks": {
            "Beginner": [
                {
                    "question": "What is a Deadlock in an operating system?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are the Coffman Conditions (the 4 necessary conditions for a deadlock to occur)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between Deadlock and Starvation?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is a Resource Allocation Graph (RAG) and how does a cycle indicate deadlock in single-instance resources?",
                    "question_type": "Practical"
                },
                {
                    "question": "What are the four primary strategies for handling deadlocks (Ignore, Prevent, Avoid, Detect & Recover)?",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "How can you prevent deadlocks by invalidating each of the four Coffman conditions?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain Deadlock Avoidance and what constitutes a Safe State vs an Unsafe State.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain the Banker\\'s Algorithm for deadlock avoidance: describe Allocation, Max, Need, and Available matrices.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How does Deadlock Detection and Recovery work when cycles are detected in wait-for graphs?",
                    "question_type": "Practical"
                },
                {
                    "question": "Given 5 processes and 3 resource types with an allocation state, run the Banker\\'s Safety Algorithm to verify if a safe sequence exists.",
                    "question_type": "Coding"
                }
            ],
            "Advanced": [
                {
                    "question": "What is the Ostrich Algorithm and why do general-purpose OSes like Linux and Windows adopt it for deadlock handling?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "How do distributed systems detect deadlocks (Edge-Chasing / Chandy-Misra-Haas algorithm)?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain lock ordering hierarchies and static code analysis tools (like Clang Thread Safety Analysis) for compile-time deadlock prevention.",
                    "question_type": "Practical"
                },
                {
                    "question": "Analyze priority inheritance vs priority ceiling protocols in preventing deadlock and priority inversion in RTOS.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Design an automatic deadlock detection watchdog thread that analyzes active lock acquisition trees and triggers thread dump diagnostics.",
                    "question_type": "Coding"
                }
            ]
        },
        "Memory Management": {
            "Beginner": [
                {
                    "question": "What is the difference between Logical (Virtual) Address and Physical Address?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the Memory Management Unit (MMU) and how does it translate virtual addresses to physical addresses?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is Fragmentation? Explain Internal Fragmentation vs External Fragmentation.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are dynamic memory allocation algorithms: First Fit, Best Fit, and Worst Fit?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is Paging in operating systems and what is the difference between a page and a frame?",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "How does Page Table address translation work (Page Number + Page Offset)?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is the Translation Lookaside Buffer (TLB) and what is a TLB Hit vs TLB Miss?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is Segmentation in memory management and how does it differ from Paging?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain Multi-Level (Hierarchical) Paging and why it is required for 64-bit address spaces.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Calculate the Effective Memory Access Time (EMAT) given TLB hit ratio and memory access latency.",
                    "question_type": "Coding"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain Inverted Page Tables and Hashed Page Tables: how do they scale with physical memory rather than virtual space?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are Huge Pages (Transparent Huge Pages - THP) in Linux and how do they reduce TLB miss rates in memory-intensive databases?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How does Kernel Page-Table Isolation (KPTI) mitigate Meltdown and Spectre speculative execution CPU vulnerabilities?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Analyze NUMA (Non-Uniform Memory Access) memory allocation policies (`numactl`, local vs remote memory node latency).",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Explain page table walk hardware microarchitecture in x86-64 (CR3 register, PML4, PDPT, PD, PT).",
                    "question_type": "Conceptual"
                }
            ]
        },
        "Virtual Memory": {
            "Beginner": [
                {
                    "question": "What is Virtual Memory and what major benefits does it provide to running processes?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is Demand Paging and what is a Page Fault?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What steps does the OS take when a Page Fault trap occurs?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is a Swap Space / Paging File on disk?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is Thrashing in an operating system?",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "Explain Page Replacement Algorithms: FIFO, Optimal (OPT/Belady), and Least Recently Used (LRU).",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is Belady\\'s Anomaly in FIFO page replacement?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain the Clock (Second-Chance) Page Replacement algorithm using the reference bit.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is the Working Set Model and how does it monitor a process\\'s locality to prevent thrashing?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Given a page reference string and 3 memory frames, calculate the number of page faults using LRU.",
                    "question_type": "Coding"
                }
            ],
            "Advanced": [
                {
                    "question": "How does Linux Out-Of-Memory (OOM) Killer calculate `oom_score` to terminate processes when physical RAM and swap are exhausted?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain dirty page writeback daemons (kswapd, pdflush) and kernel swappiness tuning.",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "What is zero-page optimization and lazy allocation: why does `malloc()` succeed even if physical memory is not yet committed?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Analyze memory ballooning and hypervisor memory overcommit in virtualized cloud environments (KVM, ESXi).",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Implement an approximation of the LRU page replacement algorithm using a bit-aging counter scheme.",
                    "question_type": "Coding"
                }
            ]
        },
        "File Systems": {
            "Beginner": [
                {
                    "question": "What is a File System and what are the standard file attributes and operations?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is an Inode in Unix/Linux file systems and what metadata does it store?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between a Hard Link and a Soft Link (Symbolic Link) in Linux?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is the difference between absolute path and relative path?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are standard file permissions (`rwx`) in Unix and what does `chmod 755` mean?",
                    "question_type": "Practical"
                }
            ],
            "Intermediate": [
                {
                    "question": "Explain File Allocation Methods: Contiguous Allocation, Linked Allocation, and Indexed Allocation.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is a Journaling File System (e.g. ext4, NTFS) and how does it prevent filesystem corruption after crashes?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does Free Space Management work using Bitmaps, Free Linked Lists, and Grouping?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is the Virtual File System (VFS) abstraction layer in modern operating systems?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What happens when you delete an open file in Linux while a process is still reading from it?",
                    "question_type": "Scenario-based"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain Copy-On-Write (COW) modern file systems like ZFS and Btrfs: snapshots, checksumming, and scrub operations.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Analyze disk I/O elevator scheduling algorithms (NOOP, Deadline, CFQ, BFQ, Kyber for NVMe SSDs).",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How does the Linux Page Cache unify file I/O caching with virtual memory buffers (`buffer_head` / `bio`)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Discuss distributed network file systems: NFS v4 vs Ceph vs GlusterFS architecture.",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "How do SSD TRIM commands and Flash Translation Layer (FTL) wear-leveling algorithms prevent write amplification?",
                    "question_type": "Conceptual"
                }
            ]
        }
    },
    "Computer Networks": {
        "OSI Model": {
            "Beginner": [
                {
                    "question": "What is the OSI (Open Systems Interconnection) 7-Layer Reference Model? Name all seven layers from physical to application.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the primary function of the Data Link Layer and what is a MAC address?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between the Network Layer (Layer 3) and Transport Layer (Layer 4)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is Encapsulation and Decapsulation as a packet moves down and up the protocol stack?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "At which OSI layer do Routers, Switches, and Hubs operate?",
                    "question_type": "Practical"
                }
            ],
            "Intermediate": [
                {
                    "question": "Compare the 7-Layer OSI Model with the 4-Layer TCP/IP Model.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are Protocol Data Units (PDUs): Frame, Packet, Segment, and Data?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain the Presentation Layer: data formatting, encryption (SSL/TLS), and compression.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What causes Layer 2 switching loops and how does the Spanning Tree Protocol (STP) prevent them?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain Flow Control vs Error Control at the Transport Layer vs Data Link Layer.",
                    "question_type": "Conceptual"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain how modern Layer 3 switches perform hardware packet forwarding using ASICs and TCAM (Ternary Content Addressable Memory).",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do Software-Defined Networking (SDN) architectures decouple the Control Plane from the Data Plane (OpenFlow)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Analyze packet path through the Linux network subsystem from NIC ring buffer interrupt to user-space socket.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain eBPF (Extended Berkeley Packet Filter) and XDP (eXpress Data Path) for programmable kernel packet processing.",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "How do network overlays (VXLAN, GENEVE) encapsulate Layer 2 frames in Layer 3 UDP packets for cloud multi-tenancy?",
                    "question_type": "Conceptual"
                }
            ]
        },
        "TCP/IP": {
            "Beginner": [
                {
                    "question": "What are the core differences between TCP (Transmission Control Protocol) and UDP (User Datagram Protocol)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain the TCP Three-Way Handshake (SYN, SYN-ACK, ACK) used to establish a connection.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Why is TCP called a reliable, connection-oriented, byte-stream protocol?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are port numbers and what is the difference between well-known ports (0-1023) and ephemeral ports?",
                    "question_type": "Practical"
                },
                {
                    "question": "Name three common protocols that use TCP and three protocols that use UDP.",
                    "question_type": "Practical"
                }
            ],
            "Intermediate": [
                {
                    "question": "Explain TCP Four-Way Handshake for connection termination (FIN, ACK, FIN, ACK) and the `TIME_WAIT` state.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain TCP Flow Control: how does the Sliding Window mechanism use the Receiver Window (`rwnd`) to avoid buffer overrun?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain TCP Congestion Control algorithms: Slow Start, Congestion Avoidance, Fast Retransmit, and Fast Recovery.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is the purpose of the TCP Checksum and how does it detect packet corruption?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is a SYN Flood DDoS attack and how do SYN Cookies mitigate it without allocating server socket state?",
                    "question_type": "Scenario-based"
                }
            ],
            "Advanced": [
                {
                    "question": "Compare modern TCP congestion algorithms: Loss-based (Cubic) vs Delay-based/Bandwidth-based (BBR - Bottleneck Bandwidth and RTT).",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain Head-of-Line (HoL) Blocking in TCP and how HTTP/3 built on QUIC (over UDP) completely eliminates it.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is TCP Selective Acknowledgment (SACK) and Duplicate SACK (D-SACK)?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Analyze TCP connection tuning for high-bandwidth delay product (BDP) networks: window scale options and buffer sizing.",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Explain TCP Fast Open (TFO) and how it enables payload transmission inside the initial SYN packet.",
                    "question_type": "Conceptual"
                }
            ]
        },
        "IP Addressing": {
            "Beginner": [
                {
                    "question": "What is an IP address and what is the difference between IPv4 (32-bit) and IPv6 (128-bit)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is a Subnet Mask and what does it separate in an IP address (Network ID vs Host ID)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are Private IP address ranges (RFC 1918) for Class A, B, and C?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is the purpose of the Loopback IP address (`127.0.0.1` / `::1`)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What does a Default Gateway do in a local area network?",
                    "question_type": "Practical"
                }
            ],
            "Intermediate": [
                {
                    "question": "Explain CIDR (Classless Inter-Domain Routing) notation (e.g. `192.168.1.0/24`) and calculate usable host counts.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Given an IP address `172.16.0.0/16`, subnet it to create 4 equal-sized subnets and identify network, broadcast, and host ranges.",
                    "question_type": "Coding"
                },
                {
                    "question": "What is NAT (Network Address Translation) and PAT (Port Address Translation / NAT Overload)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is DHCP (Dynamic Host Configuration Protocol) and explain the DORA process (Discover, Offer, Request, Acknowledge).",
                    "question_type": "Practical"
                },
                {
                    "question": "What is ARP (Address Resolution Protocol) and what is ARP spoofing/poisoning?",
                    "question_type": "Scenario-based"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain IPv6 auto-configuration: SLAAC (Stateless Address Autoconfiguration) vs Stateful DHCPv6.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does BGP Anycast routing deliver traffic to the geographically nearest server sharing the same IP address (used by Cloudflare/DNS)?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Analyze IP packet fragmentation and reassembly: MTU (Maximum Transmission Unit), Path MTU Discovery (PMTUD), and DF bit.",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Explain Variable Length Subnet Masking (VLSM) and route summarization (supernetting) to shrink router routing tables.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How do IPv4-to-IPv6 transition mechanisms work: Dual-Stack, Tunneling (6to4, Teredo), and Translation (NAT64/DNS64)?",
                    "question_type": "Conceptual"
                }
            ]
        },
        "DNS": {
            "Beginner": [
                {
                    "question": "What is DNS (Domain Name System) and why is it often called the phonebook of the internet?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between a Recursive DNS Resolver and an Authoritative DNS Server?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What do standard DNS record types do: `A`, `AAAA`, `CNAME`, `MX`, and `TXT`?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is DNS TTL (Time To Live) and how does it control caching?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the function of the local `hosts` file on Windows and Linux machines?",
                    "question_type": "Practical"
                }
            ],
            "Intermediate": [
                {
                    "question": "Walk through the complete step-by-step resolution of `www.example.com` from browser cache to root server, TLD server, and authoritative server.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are DNS Root Servers? How many logical root servers exist and how does Anycast distribute them worldwide?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is a Reverse DNS lookup (rDNS) and what is a PTR record used for?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is DNS Cache Poisoning (DNS Spoofing) and how does DNSSEC (DNS Security Extensions) mitigate it with cryptographic signatures?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "What is Split-Horizon (Split-Brain) DNS in enterprise corporate networks?",
                    "question_type": "Conceptual"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain DoH (DNS over HTTPS) and DoT (DNS over TLS): how do they protect user privacy against ISP snooping?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does GeoDNS and latency-based DNS routing direct traffic across global multi-region cloud infrastructures?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain DNS tunneling: how can malicious actors exfiltrate sensitive data through recursive DNS queries and TXT responses?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "What is EDNS (Extension Mechanisms for DNS) and how does EDNS Client Subnet (ECS) pass client prefix info to CDNs?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Analyze DNS amplification DDoS attacks and why open resolvers should enforce Response Rate Limiting (RRL).",
                    "question_type": "Scenario-based"
                }
            ]
        },
        "HTTP and HTTPS": {
            "Beginner": [
                {
                    "question": "What is HTTP (Hypertext Transfer Protocol) and what is the difference between HTTP and HTTPS?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What default port numbers are used by HTTP and HTTPS?",
                    "question_type": "Practical"
                },
                {
                    "question": "What are SSL/TLS certificates and what role do Certificate Authorities (CAs) play?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Why is HTTP called a stateless protocol and how do cookies maintain session state?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are the common HTTP request components (Method, URI, Headers, Body)?",
                    "question_type": "Practical"
                }
            ],
            "Intermediate": [
                {
                    "question": "Explain the TLS 1.3 Handshake: how does it establish symmetric session keys using asymmetric Diffie-Hellman in 1-RTT?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What are the differences between HTTP/1.1 and HTTP/2 (Multiplexing, Binary framing, Header compression with HPACK, Server Push)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is HSTS (HTTP Strict Transport Security) and how does it prevent SSL-stripping man-in-the-middle attacks?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Explain the difference between Symmetric Encryption and Asymmetric Encryption in HTTPS.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are secure cookie attributes: `HttpOnly`, `Secure`, and `SameSite` (`Strict`, `Lax`, `None`)?",
                    "question_type": "Practical"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain HTTP/3: why did it replace TCP with QUIC over UDP, and how does it resolve Head-of-Line blocking and connection migration across WiFi/Cellular?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is Server Name Indication (SNI) and Encrypted Client Hello (ECH) in TLS?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain Mutual TLS (mTLS) authentication and its essential role in zero-trust service mesh architectures (Istio/Envoy).",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "What is Certificate Pinning and OCSP Stapling (Online Certificate Status Protocol)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Analyze web performance metrics and zero round-trip resumption (0-RTT) in TLS 1.3 along with replay attack mitigations.",
                    "question_type": "Problem-solving"
                }
            ]
        },
        "Routing": {
            "Beginner": [
                {
                    "question": "What is Routing and what is the difference between Routing and Switching?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is a Routing Table and what information is stored in its entries?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between Static Routing and Dynamic Routing?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is an Autonomous System (AS) in internet infrastructure?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the Longest Prefix Match rule used by routers when forwarding packets?",
                    "question_type": "Practical"
                }
            ],
            "Intermediate": [
                {
                    "question": "What is the difference between Interior Gateway Protocols (IGP) and Exterior Gateway Protocols (EGP)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Compare Distance-Vector routing protocols (RIP) with Link-State routing protocols (OSPF).",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does OSPF (Open Shortest Path First) use Dijkstra\\'s algorithm and link-state advertisements (LSAs)?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is the Count-to-Infinity problem in distance-vector routing and how do Split Horizon and Poison Reverse mitigate it?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is BGP (Border Gateway Protocol) and why is it described as a Path-Vector protocol?",
                    "question_type": "Conceptual"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain BGP Route Selection Algorithm and attributes: Local Preference, AS Path length, Origin, MED, and eBGP vs iBGP.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is BGP Route Hijacking and how does RPKI (Resource Public Key Infrastructure) cryptographically validate route origin?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Explain MPLS (Multi-Protocol Label Switching) and how label swapping speeds up backbone forwarding over traditional IP routing.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is Segment Routing (SR-MPLS / SRv6) and how does it implement source routing in modern software-defined carrier networks?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Analyze Equal-Cost Multi-Path (ECMP) routing and hash polarization issues across data center Clos network fabrics.",
                    "question_type": "Problem-solving"
                }
            ]
        },
        "Network Security Basics": {
            "Beginner": [
                {
                    "question": "What is the CIA Triad (Confidentiality, Integrity, Availability) in information security?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is a Firewall and what is the difference between a Packet-Filtering Firewall and a Stateful Inspection Firewall?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is a Denial of Service (DoS) attack and how does a Distributed Denial of Service (DDoS) attack differ?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is a VPN (Virtual Private Network) and how does it secure internet traffic on public networks?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is Phishing and Social Engineering in cybersecurity?",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "What is a Man-In-The-Middle (MITM) attack and what techniques (like ARP poisoning) are used to execute it?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is an Intrusion Detection System (IDS) vs an Intrusion Prevention System (IPS)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain Public Key Infrastructure (PKI): asymmetric key pairs, digital certificates, and digital signatures.",
                    "question_type": "Practical"
                },
                {
                    "question": "What is Port Scanning and how do tools like Nmap use TCP SYN scans (`-sS`) vs full connect scans?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is a DMZ (Demilitarized Zone) network architecture and why are public servers isolated in it?",
                    "question_type": "Scenario-based"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain Zero Trust Architecture (ZTA): 'Never trust, always verify' principles under NIST SP 800-207.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do Web Application Firewalls (WAF) inspect Layer 7 traffic to block OWASP Top 10 exploits (SQLi, XSS, SSRF)?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Explain IPsec architecture: Authentication Header (AH) vs Encapsulating Security Payload (ESP) in Transport vs Tunnel mode.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is DNS Amplification and NTP Amplification DDoS attack reflection, and how does BCP 38 ingress filtering stop spoofed source IPs?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Analyze Post-Quantum Cryptography (PQC) algorithms selected by NIST (CRYSTALS-Kyber, Dilithium) and why RSA/ECC are vulnerable to Shor\\'s algorithm.",
                    "question_type": "Conceptual"
                }
            ]
        }
    },
    "Artificial Intelligence and Machine Learning": {
        "AI Fundamentals": {
            "Beginner": [
                {
                    "question": "What is Artificial Intelligence and how does it differ from traditional rule-based software programming?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the Turing Test and what was it designed to measure?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between Narrow AI (Weak AI), General AI (AGI), and Super AI?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is an Intelligent Agent in AI and what is the PEAS framework (Performance, Environment, Actuators, Sensors)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are State Space Search and search trees in classical AI problem solving?",
                    "question_type": "Practical"
                }
            ],
            "Intermediate": [
                {
                    "question": "Explain the A* Search algorithm: how do cost function $g(n)$ and heuristic function $h(n)$ guide optimal pathfinding?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is heuristic admissibility and consistency in A* search?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain Minimax algorithm and Alpha-Beta Pruning in adversarial game playing.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is a Knowledge Graph and how do ontologies represent semantic domain relationships?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are Constraint Satisfaction Problems (CSP) and how do forward checking and arc consistency (AC-3) solve them?",
                    "question_type": "Practical"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain Markov Decision Processes (MDP) and the Bellman Equation for optimal state-value calculation.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How does Monte Carlo Tree Search (MCTS) operate in AlphaGo (Selection, Expansion, Simulation, Backpropagation)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain Bayesian Networks and conditional independence d-separation rules.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Discuss AI Alignment and reward hacking / specification gaming in autonomous reinforcement learning systems.",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Design an automated planning agent using PDDL (Planning Domain Definition Language) with state-action transitions.",
                    "question_type": "Coding"
                }
            ]
        },
        "Machine Learning Basics": {
            "Beginner": [
                {
                    "question": "What is Machine Learning and what are the three primary paradigms (Supervised, Unsupervised, Reinforcement Learning)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between a Training set, Validation set, and Test set in ML workflows?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is Overfitting and Underfitting in machine learning models?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the Bias-Variance Tradeoff?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is Feature Scaling and why do distance-based algorithms require Normalization or Standardization?",
                    "question_type": "Practical"
                }
            ],
            "Intermediate": [
                {
                    "question": "Explain K-Fold Cross Validation and why it is superior to a simple single train-test split.",
                    "question_type": "Practical"
                },
                {
                    "question": "What are evaluation metrics for classification: Accuracy, Precision, Recall, F1-Score, and ROC-AUC curve?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "When is Accuracy a misleading metric for evaluating an ML model (e.g. imbalanced fraud detection datasets)?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "What is Regularization (L1 Lasso vs L2 Ridge) and how does each penalize model coefficients?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain Gradient Descent optimization: learning rate tuning, batch vs stochastic (SGD) vs mini-batch gradient descent.",
                    "question_type": "Problem-solving"
                }
            ],
            "Advanced": [
                {
                    "question": "Derive the mathematical formulation of L1 Lasso regularization: why does L1 induce parameter sparsity while L2 does not?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How do advanced optimizers (Momentum, RMSprop, Adam) compute adaptive learning rates and running exponential moving averages?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain Data Leakage in ML pipelines: what forms does it take and how can it be rigorously prevented?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "What is Concept Drift and Data Drift in production ML models, and how do statistical tests (KS test, PSI) monitor it?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Discuss handling extreme class imbalance: SMOTE (Synthetic Minority Over-sampling), Focal Loss, and cost-sensitive learning.",
                    "question_type": "Scenario-based"
                }
            ]
        },
        "Supervised Learning": {
            "Beginner": [
                {
                    "question": "What is Supervised Learning and what is the difference between Regression and Classification?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain Linear Regression and how the line of best fit minimizes Mean Squared Error (MSE).",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is Logistic Regression and why is the Sigmoid activation function used to output probabilities?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does the K-Nearest Neighbors (KNN) algorithm classify a new data point?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is a Decision Tree and how does it split data at internal nodes?",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "Explain splitting criteria in Decision Trees: Information Gain (Entropy) vs Gini Impurity.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is Random Forest and how does Bagging (Bootstrap Aggregation) reduce model variance?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is Gradient Boosting (GBM, XGBoost, LightGBM) and how does it train sequential trees to correct residuals?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain Support Vector Machines (SVM): maximum margin hyperplanes, support vectors, and the Kernel Trick.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain Naive Bayes classifier: why is it called 'naive' and how does Bayes\\' Theorem compute class probabilities?",
                    "question_type": "Problem-solving"
                }
            ],
            "Advanced": [
                {
                    "question": "Derive the mathematical dual formulation of Support Vector Machines and soft margin slack variables ($C$ parameter).",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How does XGBoost optimize loss using second-order Taylor expansion (gradients and Hessians) and tree pruning?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Analyze calibration of probabilistic models: Platt Scaling vs Isotonic Regression and Brier Score evaluation.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is SHAP (Shapley Additive exPlanations) and LIME for explainable machine learning (XAI) feature attribution?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Implement a Decision Tree split selection function in Python calculating Gini Impurity from scratch.",
                    "question_type": "Coding"
                }
            ]
        },
        "Unsupervised Learning": {
            "Beginner": [
                {
                    "question": "What is Unsupervised Learning and how does it differ from Supervised Learning?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is Clustering and what are common real-world use cases (e.g. customer segmentation)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does the K-Means clustering algorithm assign points and update cluster centroids iteratively?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is Dimensionality Reduction and why is the Curse of Dimensionality a problem?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is Anomaly Detection in unsupervised machine learning?",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "How do you select the optimal number of clusters K in K-Means (Elbow Method vs Silhouette Score)?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain Principal Component Analysis (PCA): variance maximization, covariance matrix, eigenvectors, and eigenvalues.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is Hierarchical Clustering (Agglomerative vs Divisive) and how do dendrograms visualize cluster merges?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain DBSCAN (Density-Based Spatial Clustering of Applications with Noise): core points, border points, and noise.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is t-SNE (t-Distributed Stochastic Neighbor Embedding) and how does it compare with PCA for 2D visualization?",
                    "question_type": "Conceptual"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain Gaussian Mixture Models (GMM) and Expectation-Maximization (EM) soft clustering algorithm.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Analyze UMAP (Uniform Manifold Approximation and Projection): mathematical foundations in Riemannian geometry vs t-SNE.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How does Isolation Forest detect anomalies in high-dimensional tabular data in O(N log N) time?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain Autoencoders for unsupervised nonlinear dimensionality reduction and reconstruction error anomaly detection.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Implement the K-Means clustering algorithm from scratch in Python using NumPy.",
                    "question_type": "Coding"
                }
            ]
        },
        "Neural Networks": {
            "Beginner": [
                {
                    "question": "What is an Artificial Neural Network (ANN) and how does an artificial neuron (Perceptron) work?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are weights and biases in a neural network layer?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is an Activation Function and why are non-linear activation functions necessary?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain common activation functions: Sigmoid, Tanh, ReLU, and Softmax.",
                    "question_type": "Practical"
                },
                {
                    "question": "What is the difference between Forward Propagation and Loss Calculation?",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "Explain Backpropagation: how does the Chain Rule of calculus compute gradients of the loss with respect to weights?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is the Vanishing Gradient problem and Exploding Gradient problem, and why does ReLU help mitigate vanishing gradients?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is Dropout in neural networks and how does it act as an ensemble regularization technique during training?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is Batch Normalization and how does it reduce internal covariate shift and accelerate convergence?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain common loss functions: Binary Cross-Entropy, Categorical Cross-Entropy, and Mean Squared Error.",
                    "question_type": "Conceptual"
                }
            ],
            "Advanced": [
                {
                    "question": "Derive the backpropagation gradient equations for a 2-layer Multilayer Perceptron with cross-entropy loss.",
                    "question_type": "Coding"
                },
                {
                    "question": "Explain weight initialization strategies: Xavier (Glorot) vs He (Kaiming) initialization and their variance preservation proofs.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Analyze loss landscape geometry, saddle points, and local minima in non-convex high-dimensional deep learning.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are Residual Connections (Skip Connections in ResNet) and how do they allow training of 100+ layer deep networks without degradation?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain learning rate schedulers: Cosine Annealing with Warm Restarts and OneCycleLR policy.",
                    "question_type": "Practical"
                }
            ]
        },
        "Deep Learning": {
            "Beginner": [
                {
                    "question": "What is Deep Learning and how does it differ from classical shallow Machine Learning?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is a Convolutional Neural Network (CNN) and why are CNNs superior to standard feedforward networks for image processing?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are Convolutional Layers, Pooling Layers (MaxPooling), and Fully Connected Layers in a CNN?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is a Recurrent Neural Network (RNN) and what types of sequential data are RNNs designed for?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is Transfer Learning and how do pre-trained models save massive computation time?",
                    "question_type": "Practical"
                }
            ],
            "Intermediate": [
                {
                    "question": "What are Long Short-Term Memory (LSTM) networks and Gated Recurrent Units (GRU)? Explain the role of the forget, input, and output gates.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How do 2D Convolution operations work mathematically with filters, kernels, stride, and padding ('same' vs 'valid')?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain Generative Adversarial Networks (GANs): how do the Generator and Discriminator compete in a minimax game?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are Variational Autoencoders (VAEs) and how does the reparameterization trick enable backpropagation through stochastic latent spaces?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is Data Augmentation (rotation, flipping, cropping, CutMix) and how does it improve generalization?",
                    "question_type": "Practical"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain the Transformer architecture: Scaled Dot-Product Self-Attention, Multi-Head Attention, and Positional Encodings.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How do Diffusion Models (DDPM / Latent Diffusion) generate high-fidelity images via forward noising and reverse denoising U-Nets?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain model quantization (INT8, FP4) and parameter-efficient fine-tuning (LoRA, QLoRA) for deploying 70B+ LLMs.",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Analyze mixed precision training (FP16 / BF16 with FP32 master weights) using NVIDIA Tensor Cores and loss scaling.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Implement scaled dot-product attention in Python using PyTorch or NumPy from scratch.",
                    "question_type": "Coding"
                }
            ]
        },
        "Natural Language Processing": {
            "Beginner": [
                {
                    "question": "What is Natural Language Processing (NLP) and what are common tasks (Sentiment Analysis, Translation, NER)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is Tokenization, Lemmatization, and Stemming in text preprocessing?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are Stop Words and why are they often filtered out in basic text classification pipelines?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is the Bag-of-Words (BoW) model and what are its primary limitations (ignoring grammar and word order)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is TF-IDF (Term Frequency-Inverse Document Frequency) and what does it measure?",
                    "question_type": "Practical"
                }
            ],
            "Intermediate": [
                {
                    "question": "Explain Word Embeddings (Word2Vec: Skip-Gram vs CBOW, GloVe) and vector semantic arithmetic (King - Man + Woman = Queen).",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is Named Entity Recognition (NER) and how do sequence labeling models tag entities?",
                    "question_type": "Practical"
                },
                {
                    "question": "Explain subword tokenization algorithms: Byte-Pair Encoding (BPE), WordPiece, and SentencePiece.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is BERT (Bidirectional Encoder Representations from Transformers) and how does Masked Language Modeling (MLM) pretrain it?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between Encoder-only (BERT), Decoder-only (GPT), and Encoder-Decoder (T5) architectures?",
                    "question_type": "Scenario-based"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain FlashAttention and how it optimizes self-attention memory access via GPU SRAM tiling and online softmax.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How does Reinforcement Learning from Human Feedback (RLHF) and Direct Preference Optimization (DPO) align LLMs?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain Retrieval-Augmented Generation (RAG): vector embeddings, vector databases (HNSW indexing), and reranking models.",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Analyze Rotary Position Embeddings (RoPE) and ALiBi for context length extrapolation in modern large language models.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Design a low-latency production RAG system pipeline handling millions of document chunks with hybrid sparse/dense search.",
                    "question_type": "Problem-solving"
                }
            ]
        }
    },
    "Software Engineering": {
        "SDLC": {
            "Beginner": [
                {
                    "question": "What is the Software Development Life Cycle (SDLC) and what are its key stages (Planning, Analysis, Design, Implementation, Testing, Deployment, Maintenance)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the Waterfall Model and what are its strengths and weaknesses?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is a Software Requirements Specification (SRS) document?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between Functional Requirements and Non-Functional Requirements?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is a feasibility study in early software project planning?",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "Explain the V-Model (Verification and Validation Model) and how each development phase maps to a testing level.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the Spiral Model and why is it preferred for high-risk, mission-critical software projects?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How do Agile and iterative development models differ fundamentally from rigid predictive Waterfall models?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "What is Technical Debt? How does it accumulate and what strategies should engineering teams use to manage it?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Explain Software Prototyping: Throwaway Prototyping vs Evolutionary Prototyping.",
                    "question_type": "Conceptual"
                }
            ],
            "Advanced": [
                {
                    "question": "Analyze risk management frameworks in modern large-scale distributed systems development under ISO/IEC 12207 standards.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How do continuous delivery (CD) practices shift traditional SDLC boundaries through trunk-based development and feature flags?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Discuss cost estimation models: Function Point Analysis vs COCOMO II algorithmic cost estimation.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Design an enterprise governance gate process for rolling out breaking architectural changes across 50+ autonomous teams.",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Explain Site Reliability Engineering (SRE) paradigms: Error Budgets, SLIs, SLOs, and SLAs in the modern software lifecycle.",
                    "question_type": "Scenario-based"
                }
            ]
        },
        "Agile Methodology": {
            "Beginner": [
                {
                    "question": "What is Agile methodology and what are the core values of the Agile Manifesto?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is Scrum and what are the key Scrum ceremonies (Sprint Planning, Daily Standup, Sprint Review, Retrospective)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are the core roles in Scrum: Product Owner, Scrum Master, and Development Team?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is a User Story and what is the standard format ('As a [user], I want [feature] so that [benefit]')?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is a Sprint in Scrum and what is typical sprint duration?",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "What is the difference between Scrum and Kanban? When should an engineering team choose Kanban over Scrum?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "What is Story Point estimation (Planning Poker / Fibonacci sequence) and why estimate effort rather than hours?",
                    "question_type": "Practical"
                },
                {
                    "question": "What are Sprint Velocity and Burndown Charts, and how do they diagnose sprint scope creep?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is the Definition of Done (DoD) vs Acceptance Criteria (AC)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How should a team handle high-priority production bug escalations that arrive mid-sprint?",
                    "question_type": "Scenario-based"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain Scaled Agile Frameworks (SAFe, LeSS, Spotify Model) for coordinating 20+ teams working on a unified platform.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Analyze common anti-patterns in Agile teams: 'ScrumBut', weaponized velocity metrics, and fake standups.",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "How do DORA metrics (Deployment Frequency, Lead Time for Changes, Change Failure Rate, Time to Restore) quantify DevOps agility?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Design a continuous retrospective framework that transforms team friction points into measurable automated engineering improvements.",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Discuss agile contract negotiation and fixed-price vs time-and-materials tradeoffs in enterprise software delivery.",
                    "question_type": "Scenario-based"
                }
            ]
        },
        "Software Testing": {
            "Beginner": [
                {
                    "question": "What is Software Testing and what is the difference between Verification and Validation?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain the Testing Pyramid: Unit Testing, Integration Testing, and End-to-End (E2E) Testing.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between Black-Box Testing and White-Box Testing?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is Regression Testing and why is it automated in CI/CD pipelines?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is a Test Case and what are its essential elements (Preconditions, Steps, Expected Result, Actual Result)?",
                    "question_type": "Practical"
                }
            ],
            "Intermediate": [
                {
                    "question": "What is Test-Driven Development (TDD) and explain the Red-Green-Refactor cycle.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is the difference between Mocks, Stubs, and Spies in unit test isolation?",
                    "question_type": "Practical"
                },
                {
                    "question": "Explain Boundary Value Analysis (BVA) and Equivalence Partitioning in test design with an example.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is Code Coverage (Line Coverage, Branch Coverage, Mutation Coverage) and why is 100% code coverage no guarantee of zero bugs?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "What is Performance Testing: Load Testing vs Stress Testing vs Soak Testing?",
                    "question_type": "Conceptual"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain Chaos Engineering (Netflix Chaos Monkey): injecting synthetic failures to verify system resilience.",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "What is Mutation Testing (e.g. Stryker, MutPy) and how does it measure test suite quality by injecting faults into source code?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Discuss Consumer-Driven Contract Testing (Pact framework) in microservices architecture to eliminate brittle end-to-end integration environments.",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "How do Fuzz Testing (AFL, LibFuzzer) and property-based testing (Hypothesis, QuickCheck) uncover edge-case security vulnerabilities?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Design an automated canary testing and synthetic monitoring pipeline that automatically triggers automated rollbacks upon error spikes.",
                    "question_type": "Coding"
                }
            ]
        },
        "Software Design": {
            "Beginner": [
                {
                    "question": "What is Software Architecture and Software Design, and how do they differ?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is Modularity in software design and what benefits does it bring?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain High Cohesion and Low Coupling: why is this the golden rule of software design?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are SOLID design principles? Name what each letter stands for.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is DRY (Don't Repeat Yourself) and KISS (Keep It Simple, Stupid)?",
                    "question_type": "Practical"
                }
            ],
            "Intermediate": [
                {
                    "question": "Explain each principle of SOLID in detail with concrete object-oriented examples: SRP, OCP, LSP, ISP, and DIP.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is Dependency Injection (DI) and Inversion of Control (IoC)? How do they decouple dependencies?",
                    "question_type": "Practical"
                },
                {
                    "question": "Explain Clean Architecture / Hexagonal Architecture (Ports and Adapters) and dependency rule direction.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is Domain-Driven Design (DDD): Entities, Value Objects, Aggregates, Repositories, and Bounded Contexts?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the difference between synchronous RPC (gRPC/REST) vs asynchronous Event-Driven messaging in system design?",
                    "question_type": "Scenario-based"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain CQRS (Command Query Responsibility Segregation) and Event Sourcing: architecture, eventual consistency, and replayability.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How do you decompose a legacy monolithic application using the Strangler Fig pattern with zero downtime?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Analyze CAP theorem vs PACELC theorem trade-offs when designing a globally distributed collaborative document editor (like Google Docs).",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain Outbox Pattern and Change Data Capture (Debezium) for guaranteeing dual-write atomicity between database and Kafka broker.",
                    "question_type": "Coding"
                },
                {
                    "question": "Design a highly available URL shortener (like TinyURL) capable of handling 50,000 read requests per second with sub-10ms latency.",
                    "question_type": "Scenario-based"
                }
            ]
        },
        "Design Patterns": {
            "Beginner": [
                {
                    "question": "What is a Software Design Pattern and what are the three Gang of Four (GoF) categories: Creational, Structural, and Behavioral?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Explain the Singleton Pattern: when should it be used and why is it sometimes considered an antipattern?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the Factory Method Pattern and how does it decouple object creation from object usage?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the Observer Pattern and how does it implement publish-subscribe notification mechanisms?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the Adapter Pattern and provide a real-world metaphor for its usage.",
                    "question_type": "Practical"
                }
            ],
            "Intermediate": [
                {
                    "question": "What is the Builder Pattern and how does it prevent the Telescoping Constructor antipattern?",
                    "question_type": "Practical"
                },
                {
                    "question": "Explain the Strategy Pattern: write a brief snippet demonstrating dynamic runtime algorithm swapping.",
                    "question_type": "Coding"
                },
                {
                    "question": "What is the Decorator Pattern and how does it adhere to the Open-Closed Principle by extending behavior without inheritance?",
                    "question_type": "Coding"
                },
                {
                    "question": "What is the difference between the Proxy Pattern, Facade Pattern, and Adapter Pattern?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is the State Pattern and how does it eliminate deeply nested conditional switch statements?",
                    "question_type": "Problem-solving"
                }
            ],
            "Advanced": [
                {
                    "question": "Implement a thread-safe Bill Pugh Singleton or double-checked locking Singleton in Java/C++ addressing memory reordering hazards.",
                    "question_type": "Coding"
                },
                {
                    "question": "Explain the Visitor Pattern and Double Dispatch in object-oriented type systems.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How does the Chain of Responsibility pattern power web server middleware pipelines (like Express, Django, Spring filters)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Design a distributed Circuit Breaker pattern with Closed, Open, and Half-Open states and sliding window error rate calculation.",
                    "question_type": "Coding"
                },
                {
                    "question": "Discuss concurrency patterns: Producer-Consumer with bounded queues, Active Object, and Half-Sync/Half-Async.",
                    "question_type": "Scenario-based"
                }
            ]
        },
        "Version Control Concepts": {
            "Beginner": [
                {
                    "question": "What is Version Control and what is the difference between Centralized VCS (e.g. SVN) and Distributed VCS (e.g. Git)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are the three Git states/areas: Working Directory, Staging Area (Index), and Repository (`.git`)?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What do essential Git commands do: `git init`, `git add`, `git commit`, `git status`, and `git push`?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is a Git branch and what is the default branch naming convention?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is a Merge Conflict in Git and why does it occur?",
                    "question_type": "Practical"
                }
            ],
            "Intermediate": [
                {
                    "question": "Explain `git merge` vs `git rebase`: what are the trade-offs regarding commit history linearity and golden rule of rebasing?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "What is the difference between `git reset` (soft, mixed, hard) and `git revert`?",
                    "question_type": "Practical"
                },
                {
                    "question": "What is `git stash` and how do you save and restore uncommitted changes across branches?",
                    "question_type": "Practical"
                },
                {
                    "question": "Explain Git branching strategies: Git Flow vs GitHub Flow vs Trunk-Based Development.",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "What is a Pull Request (PR) or Merge Request (MR) and what role does it play in code review?",
                    "question_type": "Conceptual"
                }
            ],
            "Advanced": [
                {
                    "question": "Explain Git\\'s internal content-addressable storage model: SHA-1/SHA-256 hashes, Blobs, Trees, Commits, and Annotated Tags.",
                    "question_type": "Conceptual"
                },
                {
                    "question": "How does `git bisect` use binary search to locate the exact commit that introduced a production regression bug?",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How can you recover accidentally deleted branches or commits using `git reflog`?",
                    "question_type": "Practical"
                },
                {
                    "question": "Explain Git Submodules vs Git Subtrees for managing third-party monorepo code dependencies.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "How do Git Hooks (pre-commit, commit-msg, pre-push) enforce automated linting, secret scanning, and commit conventions?",
                    "question_type": "Coding"
                }
            ]
        },
        "Software Maintenance": {
            "Beginner": [
                {
                    "question": "What is Software Maintenance and what percentage of total software lifecycle cost is typically spent on maintenance?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What are the four types of Software Maintenance: Corrective, Adaptive, Perfective, and Preventive?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is a Patch or Hotfix and how is it deployed to production?",
                    "question_type": "Practical"
                },
                {
                    "question": "Why is code documentation and clean self-documenting code vital for long-term maintenance?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is software legacy code and why is modifying legacy code often risky?",
                    "question_type": "Conceptual"
                }
            ],
            "Intermediate": [
                {
                    "question": "What is Code Refactoring? Name three common code smells (Long Method, God Class, Feature Envy) and refactoring techniques to fix them.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain Software Reverse Engineering and Re-engineering: how do they differ?",
                    "question_type": "Conceptual"
                },
                {
                    "question": "What is Software Obsolescence and Dependency EOL (End of Life) management?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "What are MTBF (Mean Time Between Failures) and MTTR (Mean Time To Repair) reliability metrics?",
                    "question_type": "Practical"
                },
                {
                    "question": "Explain the role of automated continuous integration (CI) test suites as safety nets during large-scale refactoring.",
                    "question_type": "Scenario-based"
                }
            ],
            "Advanced": [
                {
                    "question": "How do you safely refactor a mission-critical database schema under heavy 24/7 load using the Expand-Contract (Parallel Run) pattern?",
                    "question_type": "Scenario-based"
                },
                {
                    "question": "Analyze software aging, memory resource fragmentation, and software rejuvenation techniques in continuous server processes.",
                    "question_type": "Problem-solving"
                },
                {
                    "question": "Explain Lehman\\'s Laws of Software Evolution (Continuing Change, Increasing Complexity, Self-Regulation).",
                    "question_type": "Conceptual"
                },
                {
                    "question": "Design an automated dependency upgrade pipeline with Dependabot / Renovate that auto-merges patch releases passing full integration test suites.",
                    "question_type": "Coding"
                },
                {
                    "question": "How do distributed tracing (OpenTelemetry, Jaeger) and structured telemetry logs pinpoint regressions in production microservices?",
                    "question_type": "Problem-solving"
                }
            ]
        }
    }
}

# ============================================================================
# TECHNICAL EVALUATION RUBRICS & ENRICHMENT ENGINE
# ============================================================================

CURATED_QUESTION_RUBRICS = {
    "Explain the difference between mutable and immutable data types in Python with examples.": {
        "expected_answer": "Mutable data types can have their state or contents modified in-place after creation without changing their identity (memory address), such as lists, dictionaries, and sets. Immutable data types cannot be modified after creation; any modification operation constructs a new object in memory with a new identity, such as integers, floats, strings, and tuples. Modifying a mutable object preserves references, whereas modifying an immutable object rebinds the variable reference.",
        "key_concepts": ["mutable", "immutable", "in-place modification", "memory address", "lists", "dictionaries", "strings", "tuples", "rebind"],
        "important_points": [
            "Mutable objects allow in-place modification (e.g., list.append, dict[key]=val).",
            "Immutable objects cannot be altered; operations return a new object (e.g., str concatenation).",
            "Examples of mutable: list, dict, set. Examples of immutable: int, float, str, tuple, frozenset.",
            "Immutability guarantees hashability for dictionary keys and set elements."
        ],
        "common_mistakes": [
            "Believing tuples are mutable if they contain mutable objects (the tuple itself is immutable).",
            "Confusing variable rebinding (x = x + 1) with in-place mutation.",
            "Stating that strings or numbers can be modified in-place."
        ]
    },
    "What are Python's key features and why is it considered an interpreted language?": {
        "expected_answer": "Python is a high-level, dynamically typed, multi-paradigm language known for readable syntax, automatic memory management via garbage collection, and an extensive standard library. It is considered an interpreted language because Python source code is first compiled into intermediate bytecode (.pyc), which is then executed line-by-line by the Python Virtual Machine (PVM) runtime interpreter rather than compiling directly to native machine code.",
        "key_concepts": ["interpreted", "bytecode", "python virtual machine", "pvm", "dynamically typed", "garbage collection", "high-level"],
        "important_points": [
            "Source code is compiled to intermediate bytecode (.pyc) before interpretation.",
            "The PVM (Python Virtual Machine) interprets and executes bytecode line-by-line.",
            "Dynamic typing and automatic memory management provide high productivity at the cost of execution speed.",
            "Multi-paradigm support includes object-oriented, procedural, and functional styles."
        ],
        "common_mistakes": [
            "Claiming Python has no compilation step whatsoever (it compiles to bytecode).",
            "Confusing dynamic typing with weak typing (Python is dynamically but strongly typed)."
        ]
    },
    "What are the four pillars of OOP and how are classes created in Python?": {
        "expected_answer": "The four pillars of OOP are Encapsulation (bundling data and methods while restricting direct access), Abstraction (hiding implementation complexity behind clean interfaces), Inheritance (deriving new classes from existing ones for code reuse), and Polymorphism (allowing different classes to respond to the same interface in specific ways). In Python, classes are defined using the 'class' keyword, initialized with the '__init__' constructor method, and receive the instance reference via 'self'.",
        "key_concepts": ["encapsulation", "abstraction", "inheritance", "polymorphism", "class keyword", "__init__", "self", "objects"],
        "important_points": [
            "Four pillars: Encapsulation, Abstraction, Inheritance, and Polymorphism.",
            "Classes are created using 'class ClassName:' syntax.",
            "The '__init__' method serves as the constructor to initialize instance attributes.",
            "'self' represents the instance of the class and must be explicitly declared as the first parameter of instance methods."
        ],
        "common_mistakes": [
            "Omitting 'self' from method definitions in Python.",
            "Confusing Abstraction (hiding complexity) with Encapsulation (binding data and restricting access).",
            "Thinking '__init__' creates the object (it initializes it; '__new__' creates it)."
        ]
    },
    "What is the difference between '==' and 'is' operators in Python?": {
        "expected_answer": "The '==' operator checks for equality of value (whether two objects contain the same data by invoking their '__eq__' method). The 'is' operator checks for identity (whether two variable references point to the exact same object in memory by comparing their memory addresses using 'id()'). For instance, two distinct lists with identical elements [1, 2] will evaluate to True for '==' but False for 'is'.",
        "key_concepts": ["equality", "identity", "value comparison", "memory address", "id()", "is operator", "== operator", "__eq__"],
        "important_points": [
            "'==' compares values or contents of objects by calling '__eq__'.",
            "'is' checks whether two variables refer to the identical object in memory (id(a) == id(b)).",
            "Identical values in different memory locations evaluate to True for == but False for is.",
            "'is' should typically be used for singleton comparisons like 'x is None'."
        ],
        "common_mistakes": [
            "Using '==' to check for 'None' instead of 'is None'.",
            "Assuming small integer or string interning means 'is' should be used for value comparisons."
        ]
    },
    "Explain Method Resolution Order (MRO) in Python multiple inheritance and the C3 linearization algorithm.": {
        "expected_answer": "Method Resolution Order (MRO) defines the exact order in which base classes are searched when looking up methods and attributes in multiple inheritance hierarchies. Python uses the C3 Linearization algorithm to compute MRO, ensuring three key properties: local precedence order (subclasses precede base classes), monotonicity (a parent class's ordering is preserved across all descendants), and avoiding cyclic inheritance conflicts. MRO can be inspected on any class using the '__mro__' attribute or 'ClassName.mro()'.",
        "key_concepts": ["mro", "method resolution order", "c3 linearization", "multiple inheritance", "monotonicity", "local precedence", "__mro__", "super()"],
        "important_points": [
            "MRO determines the order in which classes are scanned when a method is invoked.",
            "Python 2.3+ uses the C3 Linearization algorithm to construct a deterministic, monotonic inheritance order.",
            "C3 guarantees that subclasses appear before their parents and preserves the order specified in class definitions.",
            "Accessible via ClassName.__mro__ or ClassName.mro()."
        ],
        "common_mistakes": [
            "Thinking Python uses simple depth-first or breadth-first search for multiple inheritance (it uses C3).",
            "Believing multiple inheritance causes arbitrary diamond problem ambiguities in Python."
        ]
    },
    "Explain Python's Global Interpreter Lock (GIL) and its implications on CPU-bound multithreading.": {
        "expected_answer": "The Global Interpreter Lock (GIL) is a mutex used by the standard CPython implementation to synchronize thread execution such that only one native thread executes Python bytecode at any given moment. This design prevents race conditions and ensures thread safety for CPython's reference-counting memory management. Consequently, CPU-bound multithreaded Python programs do not achieve true parallelism across multiple CPU cores; developers must use multiprocessing, native C extensions, or asynchronous I/O to achieve parallel execution for CPU-intensive workloads.",
        "key_concepts": ["gil", "global interpreter lock", "cpython", "mutex", "cpu-bound", "multithreading", "parallelism", "reference counting", "multiprocessing"],
        "important_points": [
            "The GIL allows only one thread to execute Python bytecode at a time in CPython.",
            "Designed to simplify thread-safe reference counting and avoid race conditions in memory management.",
            "CPU-bound tasks suffer performance bottlenecks in multithreaded code due to lock contention.",
            "I/O-bound tasks still benefit from multithreading because threads release the GIL during I/O operations.",
            "Parallel CPU-bound execution requires the 'multiprocessing' module or alternative runtimes."
        ],
        "common_mistakes": [
            "Believing the GIL prevents threads from running entirely (threads alternate, but do not execute bytecode simultaneously).",
            "Claiming multithreading is useless in Python (it is highly effective for I/O-bound tasks).",
            "Assuming all Python implementations have a GIL (Jython and IronPython do not)."
        ]
    },
    "Explain ACID properties in DBMS and their significance in transaction management.": {
        "expected_answer": "ACID properties define the four fundamental guarantees of reliable database transactions: Atomicity (the transaction is all-or-nothing; if any operation fails, the entire transaction rolls back), Consistency (transactions bring the database from one valid state to another satisfying all schema constraints), Isolation (concurrent transactions execute independently without interference, controlled by isolation levels), and Durability (once committed, changes are permanently written to non-volatile storage and survive system crashes).",
        "key_concepts": ["acid", "atomicity", "consistency", "isolation", "durability", "transactions", "rollback", "commit", "concurrency control"],
        "important_points": [
            "Atomicity: All operations in a transaction succeed together, or all are rolled back.",
            "Consistency: Database integrity constraints (foreign keys, checks) are maintained before and after transactions.",
            "Isolation: Intermediate states of concurrent transactions are hidden from each other (e.g., Read Committed, Serializable).",
            "Durability: Committed transactions persist permanently in storage via write-ahead logging (WAL) even across power outages."
        ],
        "common_mistakes": [
            "Confusing Consistency in ACID with Consistency in CAP theorem.",
            "Thinking Isolation means transactions cannot run concurrently (isolation levels allow managed concurrency).",
            "Believing atomicity alone guarantees database validity without consistency constraints."
        ]
    },
    "What is the difference between TCP and UDP protocols and when would you use each?": {
        "expected_answer": "TCP (Transmission Control Protocol) is a connection-oriented, reliable transport protocol that uses a 3-way handshake, sequence numbers, acknowledgments, and retransmissions to guarantee in-order, error-free packet delivery with congestion control, making it ideal for web browsing (HTTP/HTTPS), email (SMTP), and file transfer. UDP (User Datagram Protocol) is a connectionless, lightweight, unreliable transport protocol that transmits datagrams without handshakes or delivery guarantees, minimizing latency and overhead, making it ideal for real-time applications such as video streaming, VoIP, DNS lookups, and multiplayer gaming.",
        "key_concepts": ["tcp", "udp", "connection-oriented", "connectionless", "reliability", "three-way handshake", "acknowledgments", "latency", "streaming"],
        "important_points": [
            "TCP establishes connections via a 3-way handshake (SYN, SYN-ACK, ACK); UDP sends packets without connection setup.",
            "TCP guarantees delivery, packet ordering, and flow/congestion control; UDP does not guarantee packet arrival or ordering.",
            "TCP has higher header overhead (20-60 bytes); UDP has minimal header overhead (8 bytes).",
            "Use TCP when data accuracy is critical; use UDP when low latency and speed take precedence over occasional packet loss."
        ],
        "common_mistakes": [
            "Stating UDP is always faster than TCP without mentioning packet loss tolerance.",
            "Believing TCP sends datagrams while UDP sends byte streams (TCP is stream-oriented; UDP is datagram-oriented)."
        ]
    },
    "What is the difference between Primary Key and Unique Key in SQL?": {
        "expected_answer": "A Primary Key uniquely identifies each row in a database table and strictly rejects NULL values, with each table permitted only one Primary Key (which automatically creates a clustered index by default in many RDBMSs). A Unique Key also enforces uniqueness across rows but permits one (or more, depending on the SQL engine) NULL value, and a single table can define multiple Unique Key constraints.",
        "key_concepts": ["primary key", "unique key", "null values", "clustered index", "uniqueness", "table constraint"],
        "important_points": [
            "A table can have only one Primary Key, but multiple Unique Keys.",
            "Primary Key columns cannot contain NULL values; Unique Key columns can typically accept NULL values.",
            "Primary Keys generally create a clustered index by default, whereas Unique Keys typically create non-clustered indexes.",
            "Both constraints enforce entity integrity and prevent duplicate values."
        ],
        "common_mistakes": [
            "Believing Unique Keys cannot accept any NULL values in SQL standards.",
            "Thinking a table can have multiple Primary Keys (it can have a composite primary key, but only one primary key constraint)."
        ]
    },
    "What is virtual memory and how does paging work in modern Operating Systems?": {
        "expected_answer": "Virtual memory is an OS memory management capability that provides an illusion of a large, contiguous address space to processes by abstracting physical RAM through secondary storage (swap/pagefile). Paging divides virtual memory into fixed-size blocks called pages (typically 4 KB) and physical memory into matching blocks called page frames. The Memory Management Unit (MMU) uses page tables and the Translation Lookaside Buffer (TLB) to map virtual addresses to physical frames. When a requested page is not in RAM, a page fault interrupt occurs, triggering the OS to load the page from disk into a frame.",
        "key_concepts": ["virtual memory", "paging", "pages", "page frames", "page table", "mmu", "page fault", "tlb", "swap space"],
        "important_points": [
            "Virtual memory abstracts physical RAM, providing process isolation and larger addressable memory.",
            "Paging splits virtual addresses into fixed-size pages and maps them to physical page frames.",
            "The MMU performs hardware address translation with caching support from the TLB.",
            "Page faults occur when referencing a page not currently residing in physical RAM, prompting disk retrieval."
        ],
        "common_mistakes": [
            "Confusing paging (fixed-size blocks) with segmentation (variable-size logical blocks).",
            "Thinking page faults are program errors or fatal crashes (they are normal OS hardware interrupts)."
        ]
    }
}

def synthesize_rubric(question_text: str, domain: str, skill: str, difficulty: str, question_type: str) -> Dict[str, Any]:
    """
    Intelligently synthesizes an accurate evaluation rubric for any question not explicitly curated.
    Ensures complete coverage across all domains and skills.
    """
    clean_q = re.sub(r"[^\w\s]", "", question_text)
    words = [w for w in clean_q.split() if len(w) > 3 and w.lower() not in {
        "what", "which", "explain", "describe", "difference", "between", "python",
        "java", "does", "with", "examples", "write", "code", "snippet", "briefly"
    }]
    
    # Extract top keywords from question text
    core_terms = words[:4] if words else [skill]
    
    # Key concepts synthesis
    concepts = list(set([skill, domain] + core_terms))[:6]
    
    # Important points synthesis
    important_pts = [
        f"Accurately explain the core concept and technical definition of '{' '.join(core_terms[:2])}'.",
        f"Describe the internal working mechanism, lifecycle, or architecture in the context of {domain}.",
        f"Discuss practical application, performance implications, or trade-offs suitable for {difficulty} level.",
        "Demonstrate correct syntax, algorithmic structure, or implementation principles."
    ]
    
    # Common mistakes synthesis
    common_mistakes = [
        f"Giving a superficial or purely conversational response without specific {domain} technical terminology.",
        "Confusing basic conceptual syntax with internal execution mechanisms or best practices.",
        "Omitting key performance trade-offs, edge cases, or exception handling considerations."
    ]
    
    # Expected answer model synthesis
    expected_ans = (
        f"A comprehensive answer to '{question_text}' should first establish a precise technical definition of "
        f"{' '.join(core_terms[:3])} within {skill}. It should explain the underlying working mechanism, how it integrates "
        f"with {domain} architectures, and its practical implementation at the {difficulty} level. "
        f"Finally, it should address key considerations such as efficiency, error handling, and trade-offs."
    )
    
    return {
        "expected_answer": expected_ans,
        "key_concepts": concepts,
        "important_points": important_pts,
        "common_mistakes": common_mistakes
    }

def enrich_question_rubric(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Guarantees that a question item contains:
    - expected_answer
    - key_concepts
    - important_points
    - common_mistakes
    - difficulty
    - skill
    - domain
    """
    q_text = item.get("question", "")
    domain = item.get("domain", "General Tech")
    skill = item.get("skill", "General")
    diff = item.get("difficulty", "Intermediate")
    q_type = item.get("question_type", "Conceptual")

    # If item already has all fields, retain them
    if "expected_answer" in item and "key_concepts" in item and "important_points" in item and "common_mistakes" in item:
        return item

    # Check curated dictionary
    curated = CURATED_QUESTION_RUBRICS.get(q_text)
    if curated:
        item["expected_answer"] = curated["expected_answer"]
        item["key_concepts"] = curated["key_concepts"]
        item["important_points"] = curated["important_points"]
        item["common_mistakes"] = curated["common_mistakes"]
        return item

    # Fallback to intelligent synthesis
    synth = synthesize_rubric(q_text, domain, skill, diff, q_type)
    item["expected_answer"] = synth["expected_answer"]
    item["key_concepts"] = synth["key_concepts"]
    item["important_points"] = synth["important_points"]
    item["common_mistakes"] = synth["common_mistakes"]
    return item

# ============================================================================
# QUESTION SELECTION ENGINE
# ============================================================================
def generate_technical_questions(
    domain: str,
    skills: List[str],
    difficulty: str = "Intermediate",
    num_questions: int = 5
) -> List[Dict[str, Any]]:
    """
    Selects relevant, diverse technical questions from the question bank.
    
    Parameters:
        domain (str): Selected primary technical domain.
        skills (List[str]): List of selected sub-skills/topics.
        difficulty (str): 'Beginner', 'Intermediate', or 'Advanced'.
        num_questions (int): Number of questions requested (e.g., 5, 10, 15).
        
    Returns:
        List[Dict[str, Any]]: List of question dictionaries with domain, skill,
                              difficulty, question text, and question type.
    """
    if domain not in QUESTION_BANK:
        # Fallback to closest match if exact name has slight variation
        matched_domain = None
        for d in QUESTION_BANK.keys():
            if domain.lower() in d.lower() or d.lower() in domain.lower():
                matched_domain = d
                break
        if matched_domain:
            domain = matched_domain
        else:
            return []

    domain_data = QUESTION_BANK[domain]
    
    # If no skills provided, consider all available skills in this domain
    if not skills:
        skills = list(domain_data.keys())
    else:
        # Filter to only valid skills in this domain
        skills = [s for s in skills if s in domain_data]
        if not skills:
            skills = list(domain_data.keys())

    # Validate difficulty
    valid_diffs = ["Beginner", "Intermediate", "Advanced"]
    if difficulty not in valid_diffs:
        difficulty = "Intermediate"

    # Define fallback difficulty order if target difficulty has insufficient questions
    if difficulty == "Beginner":
        difficulty_order = ["Beginner", "Intermediate", "Advanced"]
    elif difficulty == "Advanced":
        difficulty_order = ["Advanced", "Intermediate", "Beginner"]
    else:
        difficulty_order = ["Intermediate", "Beginner", "Advanced"]

    # Gather questions per skill
    per_skill_candidates: Dict[str, List[Dict[str, Any]]] = {}
    for skill in skills:
        candidates = []
        skill_data = domain_data.get(skill, {})
        
        # 1. First add exact difficulty match
        for q in skill_data.get(difficulty, []):
            item = dict(q)
            item["domain"] = domain
            item["skill"] = skill
            item["difficulty"] = difficulty
            item = enrich_question_rubric(item)
            candidates.append(item)
            
        # 2. Add fallback difficulties in prioritized order
        for fallback_diff in difficulty_order:
            if fallback_diff == difficulty:
                continue
            for q in skill_data.get(fallback_diff, []):
                item = dict(q)
                item["domain"] = domain
                item["skill"] = skill
                item["difficulty"] = fallback_diff
                item = enrich_question_rubric(item)
                candidates.append(item)

        # Shuffle candidates within this skill
        random.shuffle(candidates)
        per_skill_candidates[skill] = candidates

    # Fair distribution across multiple selected skills (round-robin)
    selected_questions: List[Dict[str, Any]] = []
    seen_texts = set()

    # Continue round-robin until we satisfy num_questions or exhaust candidates
    skill_list = list(skills)
    random.shuffle(skill_list)  # Randomize starting skill order

    progress_made = True
    while len(selected_questions) < num_questions and progress_made:
        progress_made = False
        for skill in skill_list:
            if len(selected_questions) >= num_questions:
                break
            candidates = per_skill_candidates.get(skill, [])
            while candidates:
                candidate = candidates.pop(0)
                q_text = candidate["question"]
                if q_text not in seen_texts:
                    seen_texts.add(q_text)
                    selected_questions.append(candidate)
                    progress_made = True
                    break

    # Final shuffle so questions from different skills are interspersed naturally
    random.shuffle(selected_questions)
    return selected_questions
