import { useEffect, useRef, useState } from "react";

import "./App.css";



const API_URL = "http://127.0.0.1:8000";



function App() {

  const [selectedFile, setSelectedFile] = useState(null);
  const [youtubeUrl, setYoutubeUrl] = useState("");
  const [videoPreviewUrl, setVideoPreviewUrl] = useState(null);
  const [showVideoPlayer, setShowVideoPlayer] = useState(false);
  const [theme, setTheme] = useState(() => {
  return localStorage.getItem("vidmind-theme") || "system";
  });

  const [showQuizSetup, setShowQuizSetup] = useState(false);
  const [quizQuestionCount, setQuizQuestionCount] = useState(15);
  const [quizDifficulty, setQuizDifficulty] = useState("Normal");
  const [quizTimeLimitEnabled, setQuizTimeLimitEnabled] = useState(true);
  const [quizTimeLimitMinutes, setQuizTimeLimitMinutes] = useState(10);



  useEffect(() => {
    if (!selectedFile) {
      setVideoPreviewUrl(null);
      return;
    }
    const url = URL.createObjectURL(selectedFile);
    setVideoPreviewUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [selectedFile]);


  useEffect(() => {
    const mediaQuery = window.matchMedia(
      "(prefers-color-scheme: dark)"
    );

    const applyTheme = () => {
      const activeTheme =
        theme === "system"
          ? (mediaQuery.matches ? "dark" : "light")
          : theme;

      document.documentElement.setAttribute(
        "data-theme",
        activeTheme
      );

      localStorage.setItem("vidmind-theme", theme);
    };

    applyTheme();
    mediaQuery.addEventListener("change", applyTheme);

    return () => {
      mediaQuery.removeEventListener("change", applyTheme);
    };
  }, [theme]);


  const [videoId, setVideoId] = useState(null);

  
  const [currentPage, setCurrentPage] = useState("video");
  const [quizId, setQuizId] = useState(null);
  const [quizQuestions, setQuizQuestions] = useState([]);
  const [quizAnswers, setQuizAnswers] = useState({});
  const [quizResults, setQuizResults] = useState(null);
  const [quizLoading, setQuizLoading] = useState(false);
  const [quizError, setQuizError] = useState("");
  const [quizTimeLeft, setQuizTimeLeft] = useState(null);
  const [currentQuizQuestion, setCurrentQuizQuestion] = useState(0);
  
useEffect(() => {
  if (
    currentPage !== "quiz" ||
    quizResults ||
    quizTimeLeft === null
  ) {
    return;
  }

  if (quizTimeLeft <= 0) {
    handleSubmitQuiz();
    return;
  }

  const timerId = setTimeout(() => {
    setQuizTimeLeft((previous) =>
      previous === null ? null : previous - 1
    );
  }, 1000);

  return () => clearTimeout(timerId);
}, [currentPage, quizResults, quizTimeLeft]);





  const [uploading, setUploading] = useState(false);

  const [processing, setProcessing] = useState(false);

  const [completed, setCompleted] = useState(false);



  const [progress, setProgress] = useState(0);

  const [currentStep, setCurrentStep] = useState(0);



  const [statusMessage, setStatusMessage] = useState(

    "Upload a video to get started."

  );



  const [error, setError] = useState("");



  const [question, setQuestion] = useState("");

  const [answer, setAnswer] = useState("");

  const [answerAccuracy, setAnswerAccuracy] = useState(null);

  const [sources, setSources] = useState([]);

  const [asking, setAsking] = useState(false);

  const [qaError, setQaError] = useState("");



  const [dragActive, setDragActive] = useState(false);



  const fileInputRef = useRef(null);

  const pollingRef = useRef(null);

  





  // =====================================================

  // CLEANUP POLLING WHEN COMPONENT IS DESTROYED

  // =====================================================



  useEffect(() => {

    return () => {

      if (pollingRef.current) {

        clearInterval(pollingRef.current);

      }

    };

  }, []);





  // =====================================================

  // FILE SELECTION

  // =====================================================



  const handleFileSelect = (file) => {

    if (!file) return;



    setError("");

    setCompleted(false);

    setVideoId(null);

    setProgress(0);

    setCurrentStep(0);



    setQuestion("");

    setAnswer("");

    setSources([]);

    setQaError("");



    const allowedTypes = [

      "video/mp4",

      "video/x-matroska",

      "video/avi",

      "video/quicktime",

      "video/webm"

    ];



    const extension = file.name

      .substring(file.name.lastIndexOf("."))

      .toLowerCase();



    const allowedExtensions = [

      ".mp4",

      ".mkv",

      ".avi",

      ".mov",

      ".webm"

    ];



    if (

      !allowedTypes.includes(file.type) &&

      !allowedExtensions.includes(extension)

    ) {

      setError(

        "Unsupported video format. Please select MP4, MKV, AVI, MOV or WEBM."

      );

      return;

    }



    setSelectedFile(file);



    setStatusMessage(

      `${file.name} is ready to upload.`

    );

  };





  // =====================================================

  // FILE INPUT

  // =====================================================



  const handleFileInput = (event) => {

    const file = event.target.files[0];



    handleFileSelect(file);

  };





  // =====================================================

  // DRAG EVENTS

  // =====================================================



  const handleDragOver = (event) => {

    event.preventDefault();



    setDragActive(true);

  };





  const handleDragLeave = () => {

    setDragActive(false);

  };





  const handleDrop = (event) => {

    event.preventDefault();



    setDragActive(false);



    const file = event.dataTransfer.files[0];



    handleFileSelect(file);

  };





  // =====================================================

  // FORMAT FILE SIZE

  // =====================================================



  const formatFileSize = (bytes) => {

    if (bytes === 0) return "0 Bytes";



    const units = [

      "Bytes",

      "KB",

      "MB",

      "GB",

      "TB"

    ];



    const index = Math.floor(

      Math.log(bytes) / Math.log(1024)

    );



    return (

      (bytes / Math.pow(1024, index)).toFixed(2) +

      " " +

      units[index]

    );

  };





  // =====================================================

  // FORMAT VIDEO TIMESTAMP

  // =====================================================



  const formatTimestamp = (seconds) => {



    const totalSeconds = Math.max(

      0,

      Math.floor(Number(seconds) || 0)

    );



    const minutes = Math.floor(

      totalSeconds / 60

    );



    const remainingSeconds =

      totalSeconds % 60;



    return (

      `${minutes}:` +

      `${String(remainingSeconds).padStart(2, "0")}`

    );

  };





  // =====================================================

  // REAL BACKEND STATUS POLLING

  // =====================================================



  const checkProcessingStatus = (id) => {



    // Clear any previous polling

    if (pollingRef.current) {

      clearInterval(pollingRef.current);

    }





    // Check immediately

    fetchStatus(id);





    // Then check every second

    pollingRef.current = setInterval(() => {

      fetchStatus(id);

    }, 1000);

  };





  // =====================================================

  // FETCH STATUS

  // =====================================================



  const fetchStatus = async (id) => {



    try {



      const response = await fetch(

        `${API_URL}/api/videos/${id}/status`

      );





      if (!response.ok) {

        throw new Error(

          "Unable to get processing status."

        );

      }





      const data = await response.json();





      console.log(

        "REAL BACKEND STATUS:",

        data

      );





      // -----------------------------------------------

      // REAL PROGRESS FROM BACKEND

      // -----------------------------------------------



      setProgress(

        Number(data.progress || 0)

      );





      // -----------------------------------------------

      // REAL BACKEND MESSAGE

      // -----------------------------------------------



      if (data.message) {

        setStatusMessage(

          data.message

        );

      }





      // -----------------------------------------------

      // UPLOADED

      // -----------------------------------------------



      if (data.status === "uploaded") {



        setCurrentStep(0);



        setProcessing(true);

      }





      // -----------------------------------------------

      // EXTRACTING AUDIO

      // -----------------------------------------------



      else if (

        data.status === "extracting_audio"

      ) {



        setCurrentStep(1);



        setProcessing(true);

      }





      // -----------------------------------------------

      // AUDIO EXTRACTED

      // -----------------------------------------------



      else if (

        data.status === "audio_extracted"

      ) {



        setCurrentStep(1);



        setProcessing(true);

      }





      // -----------------------------------------------

      // TRANSCRIBING

      // -----------------------------------------------



      else if (

        data.status === "transcribing"

      ) {



        setCurrentStep(2);



        setProcessing(true);

      }
// ADD THIS NEW BLOCK
      else if (
        [
          "transcribed",
          "chunking",
          "chunked",
          "embedding",
          "embedded",
          "storing_vectors",
          "vector_stored"
        ].includes(data.status)
      ) {
        setCurrentStep(2);
        setProcessing(true);
      }




      // -----------------------------------------------

      // COMPLETED

      // -----------------------------------------------



      else if (

        data.status === "completed"

      ) {



        if (pollingRef.current) {

          clearInterval(

            pollingRef.current

          );

        }



        pollingRef.current = null;





        setProgress(100);



        setCurrentStep(3);



        setProcessing(false);



        setCompleted(true);



        setStatusMessage(

          "Video processing completed successfully."

        );

      }





      // -----------------------------------------------

      // FAILED

      // -----------------------------------------------



      else if (

        data.status === "failed"

      ) {



        if (pollingRef.current) {

          clearInterval(

            pollingRef.current

          );

        }



        pollingRef.current = null;





        setProcessing(false);



        setCompleted(false);



        setError(

          data.message ||

          "Video processing failed."

        );



        setStatusMessage(

          "Processing failed."

        );

      }



        } catch (err) {
      console.error("Status error:", err);

      if (!processing) {
        setError("Unable to connect to the backend.");
      }
    }
  };


  //Create Quiz
  
const handleCreateQuiz = async () => {
  if (!videoId || !completed) {
    setQuizError("Please finish processing a video first.");
    return;
  }

  setQuizLoading(true);
  setQuizError("");
  setQuizResults(null);
  setQuizQuestions([]);
  setQuizAnswers({});
  setQuizId(null);

  try {
    const response = await fetch(
      `${API_URL}/api/videos/${videoId}/quiz/generate`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question_count: quizQuestionCount,
          difficulty: quizDifficulty,
        }),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.detail || "Could not generate the quiz."
      );
    }

    setQuizId(data.quiz_id);
    setQuizQuestions(data.questions || []);
    setCurrentQuizQuestion(0);
    setQuizTimeLeft(
      quizTimeLimitEnabled
        ? quizTimeLimitMinutes * 60
        : null
    );
    setCurrentPage("quiz");
    setShowQuizSetup(false);
  } catch (error) {
    setQuizError(error.message || "Quiz generation failed.");
  } finally {
    setQuizLoading(false);
  }
};

//Submit Quiz

const handleSubmitQuiz = async () => {
  if (!videoId || !quizId || quizQuestions.length === 0) {
    setQuizError("No active quiz to submit.");
    return;
  }

  setQuizLoading(true);
  setQuizError("");

  try {
    const response = await fetch(
      `${API_URL}/api/videos/${videoId}/quiz/${quizId}/submit`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          answers: quizAnswers,
        }),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.detail || "Could not submit the quiz."
      );
    }

    setQuizResults(data);
    setQuizTimeLeft(null);
  } catch (error) {
    setQuizError(error.message || "Quiz submission failed.");
  } finally {
    setQuizLoading(false);
  }
};







  // =====================================================

  // ASK QUESTION ABOUT VIDEO

  // =====================================================



  const handleAskQuestion = async () => {



    const trimmedQuestion =

      question.trim();



    if (!videoId || !completed) {



      setQaError(

        "Your video is not ready yet."

      );



      return;

    }



    if (!trimmedQuestion) {



      setQaError(

        "Please enter a question."

      );



      return;

    }



    setAsking(true);

    setQaError("");

    setAnswer("");

    setSources([]);



    try {



      const response = await fetch(

        `${API_URL}/api/videos/${videoId}/ask`,

        {

          method: "POST",

          headers: {

            "Content-Type": "application/json"

          },

          body: JSON.stringify({

            question: trimmedQuestion

          })

        }

      );



      const data =

        await response.json();



      if (!response.ok) {



        throw new Error(

          data.detail ||

          "Unable to answer the question."

        );

      }



      setAnswer(data.answer || "");
      
      setAnswerAccuracy(
       typeof data.accuracy === "number"
        ? data.accuracy
        : null
      );

      setSources(
        Array.isArray(data.sources)
          ? data.sources
          : []
      );


    } catch (err) {



      console.error(

        "Question error:",

        err

      );



      setQaError(

        err.message ||

        "Unable to get an answer."

      );



    } finally {



      setAsking(false);

    }

  };





  // =====================================================

  // UPLOAD VIDEO

  // =====================================================



  const handleUpload = async () => {



    if (!selectedFile) {



      setError(

        "Please select a video first."

      );



      return;

    }





    setError("");



    setUploading(true);



    setProcessing(false);



    setCompleted(false);



    setProgress(0);



    setCurrentStep(0);



    setStatusMessage(

      "Uploading video..."

    );





    const formData = new FormData();



    formData.append(

      "file",

      selectedFile

    );





    try {



      const response = await fetch(

        `${API_URL}/api/videos/upload`,

        {

          method: "POST",

          body: formData

        }

      );





      const data = await response.json();





      if (!response.ok) {



        throw new Error(

          data.detail ||

          "Video upload failed."

        );

      }





      console.log(

        "UPLOAD RESPONSE:",

        data

      );





      // -----------------------------------------------

      // IMPORTANT: USE REAL VIDEO ID

      // -----------------------------------------------



      setVideoId(

        data.video_id

      );





      setUploading(false);



      setProcessing(true);



      setProgress(

        Number(data.progress || 10)

      );



      setCurrentStep(0);



      setStatusMessage(

        data.message ||

        "Video uploaded. Processing started."

      );





      // -----------------------------------------------

      // START REAL STATUS POLLING

      // -----------------------------------------------



      checkProcessingStatus(

        data.video_id

      );





    } catch (err) {



      console.error(

        "Upload error:",

        err

      );





      setUploading(false);



      setProcessing(false);



      setError(

        err.message ||

        "Something went wrong."

      );



      setStatusMessage(

        "Upload failed."

      );

    }

  };



  // =====================================================
  // YOUTUBE URL UPLOAD
  // =====================================================


  const handleYouTubeUpload = async () => {
    if (!youtubeUrl.trim()) {
      setError("Please enter a YouTube URL.");
      return;
    }

    setError("");
    setUploading(true);
    setProcessing(false);
    setCompleted(false);
    setProgress(0);
    setCurrentStep(0);
    setStatusMessage("Starting YouTube download...");

    try {
      const response = await fetch(
        `${API_URL}/api/videos/youtube`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            url: youtubeUrl.trim()
          })
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "YouTube processing failed."
        );
      }

      setVideoId(data.video_id);

      checkProcessingStatus(data.video_id);

      setUploading(false);
      setProcessing(true);
      setProgress(Number(data.progress || 5));
      setCurrentStep(0);
      setStatusMessage(
        data.message || "YouTube download started."
      );
    } catch (err) {
      setUploading(false);
      setProcessing(false);
      setError(err.message || "YouTube processing failed.");
      setStatusMessage("YouTube processing failed.");
    }
  };



  // =====================================================

  // RESET

  // =====================================================



  const handleReset = () => {



    if (pollingRef.current) {

      clearInterval(

        pollingRef.current

      );

    }



    pollingRef.current = null;





    setSelectedFile(null);



    setVideoId(null);



    setUploading(false);



    setProcessing(false);



    setCompleted(false);



    setProgress(0);



    setCurrentStep(0);



    setQuestion("");

    setAnswer("");

    setSources([]);

    setQaError("");



    setError("");



    setStatusMessage(

      "Upload a video to get started."

    );





    if (fileInputRef.current) {

      fileInputRef.current.value = "";

    }

  };





  // =====================================================

  // PROCESSING STEPS

  // =====================================================



  const steps = [

    {

      icon: "📤",

      title: "Video Uploaded",

      description: "Video received by VidMind"

    },

    {

      icon: "🎵",

      title: "Audio Extraction",

      description: "Extracting audio with FFmpeg"

    },

    {

      icon: "🤖",

      title: "AI Transcription",

      description: "Whisper is understanding your video"

    },

    {

      icon: "✨",

      title: "Knowledge Ready",

      description: "Your video is ready for AI"

    }

  ];





  // =====================================================

  // UI

  // =====================================================



  return (

    <div className="app">



      {/* ============================================

          NAVBAR

      ============================================ */}



      <header className="navbar">



        <div className="brand">



          <div className="brand-icon">
          <img
             src="/vidmind-logo.png"
             alt="VidMind AI logo"
             className="brand-logo"
          />
          </div>


        </div>





        <div className="navbar-actions">

          <div className="theme-selector">
            <label htmlFor="theme-select">Theme</label>
            <select
              id="theme-select"
              value={theme}
              onChange={(event) => setTheme(event.target.value)}
            >
              <option value="system">System</option>
              <option value="light">Light</option>
              <option value="dark">Dark</option>
            </select>
          </div>

          <div className="backend-status">
            <span className="status-dot"></span>
            Backend Connected
          </div>

        </div>



      </header>





      {/* ============================================

          MAIN

      ============================================ */}


    {currentPage === "video" && (
      <main className="main-container">



        {/* HERO */}



        <section className="hero">



          <div className="hero-badge">

            ✨ AI-Powered Video Learning

          </div>



          <h2>

            Turn your videos into

            <span> knowledge.</span>

          </h2>



          <p>

            Upload a lecture, tutorial or presentation

            and let VidMind transform it into searchable

            AI-powered knowledge.

          </p>



        </section>





        {/* ========================================

            UPLOAD CARD

        ======================================== */}



        {!processing &&

        !completed && (



          <section className="upload-card">



            <div

              className={`drop-zone ${

                dragActive

                  ? "drag-active"

                  : ""

              }`}

              onDragOver={handleDragOver}

              onDragLeave={handleDragLeave}

              onDrop={handleDrop}

              onClick={() =>

                fileInputRef.current.click()

              }

            >



              <input

                ref={fileInputRef}

                type="file"

                accept="video/*"

                onChange={handleFileInput}

                hidden

              />





              <div className="upload-icon">

                ↑

              </div>





              <h3>

                Drop your video here

              </h3>





              <p>

                or click to browse your computer

              </p>





              <span className="formats">

                MP4 • MKV • AVI • MOV • WEBM

              </span>

              <div className="youtube-upload">
                <p>Or import from YouTube</p>

                <input
                  type="url"
                  placeholder="Paste YouTube video URL..."
                  value={youtubeUrl}
                  onChange={(event) =>
                    setYoutubeUrl(event.target.value)
                  }
                  onClick={(event) => event.stopPropagation()}
                />

                <button
                  type="button"
                  onClick={(event) => {
                    event.stopPropagation();
                    handleYouTubeUpload();
                  }}
                  disabled={uploading || processing}
                >
                  Import YouTube Video
                </button>
              </div>




            </div>





            {/* SELECTED FILE */}



            {selectedFile && (



              <div className="selected-file">



                <div className="file-icon">

                  🎬

                </div>



                <div className="file-info">



                  <strong>

                    {selectedFile.name}

                  </strong>



                  <span>

                    {formatFileSize(

                      selectedFile.size

                    )}

                  </span>



                </div>



                <button

                  className="remove-button"

                  onClick={(event) => {



                    event.stopPropagation();



                    setSelectedFile(null);



                  }}

                >

                  ×

                </button>



              </div>



            )}





            {/* UPLOAD BUTTON */}



            <button

              className="upload-button"

              onClick={handleUpload}

              disabled={

                !selectedFile ||

                uploading

              }

            >



              {uploading

                ? "Uploading..."

                : "🚀 Upload & Analyze"}



            </button>





            {/* STATUS */}



            <p className="small-status">

              {statusMessage}

            </p>





            {/* ERROR */}



            {error && (



              <div className="error-box">

                ⚠️ {error}

              </div>



            )}



          </section>



        )}





        {/* ========================================

            PROCESSING

        ======================================== */}



        {(processing || completed) && (



          <section className="processing-card">



            <div className="processing-header">



              <div>



                <span className="processing-label">

                  {completed

                    ? "PROCESSING COMPLETE"

                    : "PROCESSING VIDEO"}

                </span>



                <h3>

                  {completed

                    ? "Your video is ready!"

                    : "VidMind is analyzing your video"}

                </h3>



              </div>





              <div className="percentage">

                {progress}%

              </div>



            </div>





            {/* PROGRESS BAR */}



            <div className="progress-container">



              <div

                className="progress-bar"

                style={{

                  width: `${progress}%`

                }}

              ></div>



            </div>





            <div className="progress-message">



              <span>

                {statusMessage}

              </span>



              <span>

                {progress}%

              </span>



            </div>





            {/* STEPS */}



            <div className="steps">



              {steps.map(

                (step, index) => {



                  const isComplete =

                    index < currentStep ||

                    (completed &&

                      index === 3);



                  const isCurrent =

                    index === currentStep &&

                    !completed;





                  return (



                    <div

                      className={`step ${

                        isComplete

                          ? "complete"

                          : ""

                      } ${

                        isCurrent

                          ? "current"

                          : ""

                      }`}

                      key={index}

                    >



                      <div className="step-icon">



                        {isComplete

                          ? "✓"

                          : step.icon}



                      </div>





                      <div className="step-content">



                        <strong>

                          {step.title}

                        </strong>



                        <span>

                          {step.description}

                        </span>



                      </div>



                    </div>



                  );



                }

              )}



            </div>





            {completed && videoPreviewUrl && selectedFile && (
              <div className="completed-video-section">
                <button type="button" className="completed-video-preview" onClick={() => setShowVideoPlayer(true)} aria-label={"Play " + selectedFile.name}>
                  <video src={videoPreviewUrl} className="video-thumbnail" muted preload="metadata" playsInline />
                  <span className="video-play-overlay">▶</span>
                </button>
                <div className="completed-video-info">
                  <span className="completed-video-label">UPLOADED VIDEO</span>
                  <strong title={selectedFile.name}>{selectedFile.name}</strong>
                  <span>Click the preview to play</span>
                </div>
              </div>
            )}

            {completed && showVideoPlayer && videoPreviewUrl && (
              <div className="video-player-overlay" role="dialog" aria-modal="true" onClick={() => setShowVideoPlayer(false)}>
                <div className="video-player-modal" onClick={(event) => event.stopPropagation()}>
                  <div className="video-player-header">
                    <div>
                      <span className="completed-video-label">NOW PLAYING</span>
                      <strong>{selectedFile?.name}</strong>
                    </div>
                    <button type="button" className="video-player-close" onClick={() => setShowVideoPlayer(false)} aria-label="Close video player">×</button>
                  </div>
                  <video src={videoPreviewUrl} className="video-player" controls autoPlay playsInline preload="metadata" />
                </div>
              </div>
            )}

            {/* VIDEO ID */}



            {videoId && (



              <div className="video-id">



                <span>

                  Video ID

                </span>



                <code>

                  {videoId}

                </code>



              </div>



            )}





            {/* COMPLETE ACTION */}

            {completed && (
              <div className="quiz-actions">
              <button
                className="continue-button"
                onClick={handleReset}
              >
                Process Another Video →
              </button>

              <button
                className="take-quiz-button"
                type="button"
                onClick={() => setShowQuizSetup(true)}
              >
                Quiz
              </button>
              </div>
            )}



          </section>



        )}





        {/* ========================================

            VIDEO Q&A

        ======================================== */}



        {completed && (



          <section className="qa-card">



            <div className="qa-header">



              <span className="qa-label">

                VIDEO Q&A

              </span>



              <h3>

                Ask anything about this video

              </h3>



              <p>

                VidMind searches the transcript and

                uses LLM to answer from the video context.

              </p>



            </div>





            <div className="qa-input-row">



              <input

                className="qa-input"

                type="text"

                value={question}

                onChange={(event) =>

                  setQuestion(event.target.value)

                }

                onKeyDown={(event) => {



                  if (

                    event.key === "Enter" &&

                    !asking

                  ) {

                    handleAskQuestion();

                  }



                }}

                placeholder="e.g. What are the main points discussed?"

                disabled={asking}

              />



              <button

                className="qa-button"

                onClick={handleAskQuestion}

                disabled={

                  asking ||

                  !question.trim()

                }

              >

                {asking

                  ? "Thinking..."

                  : "Ask →"}

              </button>



            </div>





            {qaError && (



              <div className="qa-error">

                ⚠️ {qaError}

              </div>



            )}





            {answer && (



              <div className="answer-card">



                <div className="answer-title">
                  Answer
                </div>

                {answerAccuracy !== null && (
                  <div className="answer-accuracy">
                    Accuracy: {answerAccuracy}%
                  </div>
                )}

                <div className="answer-text">
                  {answer}
                </div>



              </div>



            )}





            {sources.length > 0 && (



              <div className="sources-card">



                <div className="sources-title">

                  Video Sources

                </div>



                <div className="sources-list">



                  {sources.map(

                    (source, index) => (



                      <div

                        className="source-item"

                        key={`${source.chunk_id || index}-${index}`}

                      >



                        <div className="source-meta">



                          <span>

                            Source {index + 1}

                          </span>



                          <span>

                            {formatTimestamp(source.start)}

                            {" – "}

                            {formatTimestamp(source.end)}

                          </span>



                        </div>



                        <p>

                          {source.text}

                        </p>



                      </div>



                    )

                  )}



                </div>



              </div>



            )}



          </section>



        )}





        {/* ========================================

            FEATURES

        ======================================== */}



        {!processing &&

        !completed && (



          <section className="features">



            <div className="feature">



              <span>🎙️</span>



              <div>

                <strong>

                  AI Transcription

                </strong>



                <p>

                  Powered by Whisper

                </p>

              </div>



            </div>





            <div className="feature">



              <span>⚡</span>



              <div>

                <strong>

                  Fast Processing

                </strong>



                <p>

                  Automated video analysis

                </p>

              </div>



            </div>





            <div className="feature">



              <span>🧠</span>



              <div>

                <strong>

                  Smart Knowledge

                </strong>



                <p>

                  Ask questions about your video

                </p>

              </div>



            </div>



          </section>



        )}



      </main>
    )}

      
      {showQuizSetup && (
        <div className="quiz-modal-overlay">
          <div className="quiz-modal">
            <button
              className="quiz-modal-close"
              onClick={() => setShowQuizSetup(false)}
              aria-label="Close quiz setup"
            >
              ×
            </button>

            <h2>Create Your Video Quiz</h2>
            <p>Customize a quiz from your processed video.</p>

            <label className="quiz-field-label">
              Number of questions
            </label>
            <div className="quiz-setting-row">
              <input
                type="range"
                min="1"
                max="100"
                value={quizQuestionCount}
                onChange={(e) =>
                  setQuizQuestionCount(Number(e.target.value))
                }
              />
              <input
                type="number"
                min="1"
                max="100"
                value={quizQuestionCount}
                onChange={(e) =>
                  setQuizQuestionCount(
                    Math.max(1, Math.min(100, Number(e.target.value) || 1))
                  )
                }
              />
            </div>

            <label className="quiz-field-label">
              Difficulty
            </label>
            <select
              className="quiz-difficulty-select"
              value={quizDifficulty}
              onChange={(e) => setQuizDifficulty(e.target.value)}
            >
              <option value="Easy">Easy</option>
              <option value="Normal">Normal</option>
              <option value="Difficult">Difficult</option>
              <option value="Extreme">Extreme</option>
            </select>

            <label className="quiz-field-label">
              Time limit
            </label>
            <div className="quiz-time-toggle">
              <button
                type="button"
                className={quizTimeLimitEnabled ? "selected" : ""}
                onClick={() => setQuizTimeLimitEnabled(true)}
              >
                Yes
              </button>
              <button
                type="button"
                className={!quizTimeLimitEnabled ? "selected" : ""}
                onClick={() => setQuizTimeLimitEnabled(false)}
              >
                No
              </button>
            </div>

            {quizTimeLimitEnabled && (
              <>
                <label className="quiz-field-label">
                  Duration (minutes)
                </label>
                <div className="quiz-setting-row">
                  <input
                    type="range"
                    min="1"
                    max="180"
                    value={quizTimeLimitMinutes}
                    onChange={(e) =>
                      setQuizTimeLimitMinutes(Number(e.target.value))
                    }
                  />
                  <input
                    type="number"
                    min="1"
                    max="180"
                    value={quizTimeLimitMinutes}
                    onChange={(e) =>
                      setQuizTimeLimitMinutes(
                        Math.max(1, Math.min(180, Number(e.target.value) || 1))
                      )
                    }
                  />
                </div>
              </>
            )}

            <button
             type="button"
              className="quiz-start-button"
              onClick={handleCreateQuiz}
             disabled={quizLoading}
            >
            {quizLoading ? "Generating Quiz..." : "Create Quiz →"}
            </button>
          </div>
        </div>
      )}

      {/* QUIZ PAGE */}
{currentPage === "quiz" && (
  <section className="quiz-page">
    <div className="quiz-page-header">
      <button
        type="button"
        className="quiz-back-button"
        onClick={() => setCurrentPage("video")}
      >
        ← Back to Video
      </button>

      <div>
        <h1>Video Quiz</h1>
        <p>
          Question {Math.min(currentQuizQuestion + 1, quizQuestions.length)}
          {" "}of {quizQuestions.length}
        </p>
      </div>

      {quizTimeLeft !== null && !quizResults && (
        <div className="quiz-countdown">
          {Math.floor(quizTimeLeft / 60)}:
          {String(quizTimeLeft % 60).padStart(2, "0")}
        </div>
      )}
    </div>

    {quizError && (
      <p className="quiz-error" role="alert">{quizError}</p>
    )}

    {quizLoading && (
      <p className="quiz-loading">Please wait…</p>
    )}

    {!quizResults && quizQuestions.length > 0 && (
      <div className="quiz-question-card">
        <div className="quiz-progress-track">
          <div
            className="quiz-progress-fill"
            style={{
              width: `${
                ((currentQuizQuestion + 1) / quizQuestions.length) * 100
              }%`,
            }}
          />
        </div>

        <h2>
          {quizQuestions[currentQuizQuestion]?.question}
        </h2>

        <div className="quiz-options">
          {Object.entries(
            quizQuestions[currentQuizQuestion]?.options || {}
          ).map(([key, value]) => (
            <button
              key={key}
              type="button"
              className={
                quizAnswers[String(currentQuizQuestion)] === key
                  ? "quiz-option selected"
                  : "quiz-option"
              }
              onClick={() =>
                setQuizAnswers((previous) => ({
                  ...previous,
                  [String(currentQuizQuestion)]: key,
                }))
              }
            >
              <span className="quiz-option-letter">{key}</span>
              <span>{value}</span>
            </button>
          ))}
        </div>

        <div className="quiz-question-navigation">
          <button
            type="button"
            disabled={currentQuizQuestion === 0}
            onClick={() =>
              setCurrentQuizQuestion((previous) => previous - 1)
            }
          >
            Previous
          </button>

          {currentQuizQuestion < quizQuestions.length - 1 ? (
            <button
              type="button"
              onClick={() =>
                setCurrentQuizQuestion((previous) => previous + 1)
              }
            >
              Next →
            </button>
          ) : (
            <button
              type="button"
              disabled={quizLoading}
              onClick={handleSubmitQuiz}
            >
              Submit Quiz
            </button>
          )}
        </div>
      </div>
    )}

    {quizResults && (
      <div className="quiz-results">
        <h2>Quiz Results</h2>
        <div className="quiz-score">
          <strong>{quizResults.score} / {quizResults.total}</strong>
          <span>{quizResults.percentage}%</span>
        </div>

        {quizResults.results.map((result, index) => (
          <article
            key={index}
            className={
              result.is_correct
                ? "quiz-review-card correct"
                : "quiz-review-card incorrect"
            }
          >
            <h3>
              {index + 1}. {result.question}
            </h3>

            <p>
              Your answer: {
                result.selected_answer
                  ? `${result.selected_answer}. ${
                      result.options[result.selected_answer] || ""
                    }`
                  : "Not answered"
              }
            </p>

            <p>
              Correct answer: {result.correct_answer}.{" "}
              {result.options[result.correct_answer]}
            </p>

            {result.explanation && <p>{result.explanation}</p>}
          </article>
        ))}

        <button
          type="button"
          className="quiz-back-button"
          onClick={() => setCurrentPage("video")}
        >
          Return to Video
        </button>
      </div>
    )}
  </section>
)}






      {/* ============================================

          FOOTER

      ============================================ */}



      <footer>



        <span>

          VidMind AI

        </span>



        <span>

          •

        </span>



        <span>

          Intelligent Video Understanding

        </span>



      </footer>



    </div>

  );

}




export default App;
