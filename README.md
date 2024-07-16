# aug-sdk

This python library allows uploading videos to [Augmend](https://augmend.com) and retrieving the documents generated from the video. In order to use the API, you'll first need to generate an API key. Create an account on Augmend and visit [https://augmend.com/settings](https://augmend.com/settings) to create an API key.

To create a client object, import `aug_sdk.video.AugmendVideoClient` and pass the API key you created. The log_callback parameter is optional but can be used to see additional progress updates. This can be useful because uploading and processing a video will take several minutes (up to an hour for longer videos). For testing purposes you can just use `print` as a parameter here.

```python
from aug_sdk.video import AugmendVideoClient

video_client = AugmendVideoClient(api_key=api_key, log_callback=print)
```

Once the video_client is created, you can upload a video with `upload_video`. The value returned is a "workspace ID" and will be used in future calls to the client when retrieving documents.

```python
wid = video_client.upload_video(video_file)
```

When this function returns, all processing will be complete and you can download individual documents. For instance, to get a generated summary of the video you can do this:

```python
doc = video_client.get_document(wid, "synopsis")
print(doc)
```

There are several document types available.

# title

The "title" document is the generated title of a video. It is returned as a string.

```python
"Expert Debugging: Breakpoints, Stack Traces, and JavaScript in WinDbg"
```

# synopsis

The "synopsis" document is a simple text description of a video. It is returned as a string.

```python
"The session covers advanced debugging techniques using WinDebug, including setting conditional breakpoints, evaluating debugger data models with the dx command, and using JavaScript for stack trace analysis. A script is created to track function call frequencies and analyze stack traces by implementing a custom StackEntry class. The discussion also touches on the use of JavaScript for creating debugger extensions and the practical application of these techniques for profiling and debugging."
```

# keywords

The "keywords" document is an array of identified keywords in the video. It is returned as an array of strings.

```python
['Windebug', 'Conditional Breakpoints', 'Stack Trace', 'Javascript Debugging', 'Profiler']
```

# chapters

The "chapters" document lists the identified chapters of a video and includes the title and synopsis of each chapter.

```python
[
    {
        'connective': [],
        'end': '1721169283.141',
        'init_focus': None,
        'keywords': ['WinDbg', 'Breakpoints', 'Scripting', 'Debugging', 'Data Model'],
        'nice_end': '00:02:53',
        'nice_start': '00:00:00',
        'segment': [0, 1, ...],
        'sot': '1721169110.0',
        'start': '1721169110.0',
        'synopsis': 'The session covers the creation and utilization of a script in WinDbg to manage breakpoints with conditions and track execution counts. It includes the use of the dx command to evaluate against the debugger data model, setting up a breakpoint with a slash-w flag to call a function without breaking, and verifying the hit count of a breakpoint within a debugging session.',
        'title': 'Advanced Breakpoint Management with WinDbg'
    },
    {
        # ...
    }
]
```

# questions

The "questions" document describes suggested questions that could be answered by the Augmend assistant generated for this video. This is returned as a list of strings.

```python
[
    'How is the slash-w flag used in conjunction with breakpoints in WinDbg?',
    'What data structure is used to represent the call hierarchy in the stack trace?',
    "How does the 'get or create child' function handle the incrementation of the node's associated count?",
    'What language was mentioned for creating debugger extensions?'
]
```

# steps/async

The "steps" and "async" documents describes each chapter in more detail. The "steps" document type assumes the video describes the steps of a process, and the "async" document assumes the video describes a status updated (e.g. someone records a status update for their team to watch later). Each step has a title and synopsis, and has a breakdown of identified subgoals.

```python
[
    {
        'nice_start': '00:00:00',
        'nice_end': '00:02:53',
        'start': '1721169110.0',
        'end': '1721169283.141',
        'sot': '1721169110.0',
        'segment': [0, 1, ...],
        'connective': [],
        'title': 'Advanced Breakpoint Management with WinDbg',
        'synopsis': 'The session covers the creation and utilization of a script in WinDbg to manage breakpoints with conditions and track execution counts. It includes the use of the dx command to evaluate against the debugger data model, setting up a breakpoint with a slash-w flag to call a function without breaking, and verifying the hit count of a breakpoint within a debugging session.',
        'keywords': ['WinDbg', 'Breakpoints', 'Scripting', 'Debugging', 'Data Model'],
        'init_focus': None,
        'subgoal': {
            'goal': 'To create a script in WinDbg that utilizes a conditional breakpoint to track the number of times a function is called.',
            'steps': [
                {
                    'desc': 'Start a debugging session on NTSD.',
                    'shell': 'ntsd.exe',
                    'screen': '00|00:00:36',
                    'attached': True,
                    'aid': 'a-spCtNZ2QAA',
                    'code': '00',
                    'hhmmss': '00:00:36'
                }, {
                    #...
                }
                    
            ],
            'notes': "The script created in WinDbg allows for tracking the number of times a specific function is called without interrupting the debugging process, which can be useful for identifying bugs. The use of the slash-w flag in setting the conditional breakpoint is a key aspect of this process, as it allows the script's function to be called while the debugger continues running. The comma-false trick is used to ensure that the debugger does not break when the conditional breakpoint is hit, thus allowing for seamless tracking. It is important to have a good understanding of the WinDbg data model and the dx command for evaluating expressions within the debugger."
        }
    },
    {
        #...
    }
]
```