# ReadingTools
is a set of Tools aimed at enhancing reading experience on iPhone, designed for [Pythonista for iOS](http://omz-software.com/pythonista/).

You can
* `TextTime.py`: estimate reading time of the text
* `Summarize.py`: extractively summarize the text
* `local_TTS.py`: locally synthesize audio file generated from the text
* `google_TTS.py`: remotely synthesize audio file with Google Cloud service, generated from the text  
(You need to run your own server to communicate with Google Cloud API, though, since Pythonista cannot directly communicate with Google API. (TBD: example RESTful API server via Flask))

There's also
* `AppleNewsUtils.py`: utilities for interacting with Apple News app.
* `Utils.py`: utilities for fetching and manipulating text from clipboard, URL, etc.
