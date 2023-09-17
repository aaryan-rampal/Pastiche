import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [isScaling, setIsScaling] = useState(false);

  const handleStartButtonHover = () => {
    setIsScaling(true);
  };

  const handleStartButtonLeave = () => {
    setIsScaling(false);
  };

  const [drawing, setDrawing] = useState(false);
  const [lines, setLines] = useState([]);
  const [showBackground, setShowBackground] = useState(true); // Track the visibility of the background
  const [currentImageIndex, setCurrentImageIndex] = useState(0); // Track the current image index
  const canvasRef = useRef(null);


  // Array of image URLs
  const imageUrls = [
    'https://qph.cf2.quoracdn.net/main-qimg-1430158d6e580c3a81372b1ad37b9fc1-lq',
    'https://i.pinimg.com/736x/ef/26/46/ef2646b821cca54a5ad1cdfcf95d2a1a.jpg',
    'https://hackthenorth.com/static/media/youbelongintech2.5e4452798b0547c2c45b.jpg',
    // Add more image URLs here
  ];

  
  useEffect(() => {
    const app = document.querySelector(".App");
    // Generate a random index to select a random image URL
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    ctx.lineWidth = 2;
    ctx.strokeStyle = 'black';

    // Set canvas width and height to match screen dimensions
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    app.addEventListener("mousemove", (e) => {
      const x = e.clientX / window.innerWidth - 0.5;
      const y = e.clientY / window.innerHeight - 0.5;
    
      app.style.backgroundPosition = `${x * 20}px ${y * 20}px`; // Adjust the multiplier for the desired effect
    });
    const changeBackgroundImage = () => {
      app.style.backgroundImage = `url(${imageUrls[currentImageIndex]})`;
      setCurrentImageIndex((prevIndex) => (prevIndex + 1) % imageUrls.length);
    };  
    

    const imageChangeInterval = setInterval(changeBackgroundImage, 10000);

    // Clean up the timer when the component unmounts
    return () => {
      clearInterval(imageChangeInterval);
    };

    
    
   
    
    
  }, [currentImageIndex]);

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    setLines([]);
  };

  const handleMouseDown = () => {
    setDrawing(true);
    clearCanvas();
    const canvas = canvasRef.current;
    canvas.style.backgroundImage = 'none';
  };

  const handleMouseUp = async() => {

    setDrawing(false);
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    setShowBackground(false); // Hide the background image
    console.log(lines);

	await axios({
	  method: 'post',
	  url: 'http://localhost:5000/process_drawing_array',
	  data: {
		  arr : lines
	  }
	})
  .then(response => {
    console.log(response, typeof (response));
  })
  };



  const handleMouseMove = (e) => {
    if (!drawing) {
      return;
    }
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const { clientX, clientY } = e;
    const { left, top } = canvas.getBoundingClientRect();
    const x = (clientX - left) / (0.95);
    const y = (clientY - top) / (0.95);

    const newLine = [...lines, { x, y }];

    if (newLine.length > 20) {
      newLine.shift();
    }

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.beginPath();
    ctx.moveTo(newLine[0].x, newLine[0].y);

    newLine.forEach((point) => {
      ctx.lineTo(point.x, point.y);
    });

    ctx.stroke();

    setLines(newLine);
  };

  const handleDarkEffectClick = () => {
    // Toggle the display property of darkEffect and canvas
    const darkEffectDiv = document.getElementById('darkEffect');
    const madeWith = document.getElementById("madeWith");
    const pencilGif = document.getElementById("pencilGif");
    const canvas = canvasRef.current;

    if (darkEffectDiv.style.display !== 'none') {
      darkEffectDiv.style.display = 'none';
      canvas.style.display = 'block';
      madeWith.style.display = 'none';
    } else {
      darkEffectDiv.style.display = 'block';
      canvas.style.display = 'none';
    }
    
  };

  return (
    <div className="App">
      <div id="darkEffect">
        <h1 id="title" onClick={handleDarkEffectClick}>PASTICHE</h1>
        <button id="startButton" onClick={handleDarkEffectClick}
        onMouseEnter={handleStartButtonHover}
        onMouseLeave={handleStartButtonLeave}>Click Here To Start Drawing</button>
      </div>
      <div id = "canvasHolder">
        <canvas
          id="canvas"
          ref={canvasRef}
          onMouseDown={handleMouseDown}
          onMouseUp={handleMouseUp}
          onMouseMove={handleMouseMove}
        />
      </div>
      <p id = "madeWith">Made with React and 🐒🧠</p>
    </div>
  );
}

export default App;
