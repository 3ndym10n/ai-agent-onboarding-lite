"""
Vision Interrogation Web Interface: Interactive web - based interface for vision definition.

This module provides a modern, responsive web interface for the enhanced vision
interrogation system, making it easy for users to define their project vision
through guided questioning.
"""

import json
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict

from .enhanced_vision_interrogator import (
    ProjectType,
    get_enhanced_vision_interrogator,
)


class VisionWebInterface:
    """Web interface for vision interrogation system."""

    def __init__(self, root: Path, port: int = 8080):
        self.root = root
        self.port = port
        self.interrogator = get_enhanced_vision_interrogator(root)
        self.server = None
        self.server_thread = None

    def start_web_interface(self) -> Dict[str, Any]:
        """Start the web interface server."""
        try:
            # Create custom request handler
            handler = self._create_request_handler()

            # Start server in a separate thread
            self.server = HTTPServer(("localhost", self.port), handler)
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()

            # Wait a moment for server to start
            time.sleep(1)

            # Open browser
            url = f"http://localhost:{self.port}"
            webbrowser.open(url)

            return {
                "status": "success",
                "message": f"Web interface started on {url}",
                "url": url,
                "port": self.port,
            }

        except Exception as e:
            return {"status": "error", "message": f"Failed to start web interface: {e}"}

    def stop_web_interface(self) -> Dict[str, Any]:
        """Stop the web interface server."""
        try:
            if self.server:
                self.server.shutdown()
                self.server.server_close()
                self.server = None

            return {"status": "success", "message": "Web interface stopped"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to stop web interface: {e}"}

    def _create_request_handler(self):
        """Create custom HTTP request handler."""
        interrogator = self.interrogator

        class VisionRequestHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/":
                    self._serve_main_page()
                elif self.path == "/api / status":
                    self._serve_status()
                elif self.path == "/api / questions":
                    self._serve_questions()
                elif self.path.startswith("/api / project - types"):
                    self._serve_project_types()
                else:
                    self._serve_404()

            def do_POST(self):
                if self.path == "/api / start":
                    self._handle_start_interrogation()
                elif self.path == "/api / submit":
                    self._handle_submit_response()
                elif self.path == "/api / complete":
                    self._handle_complete_interrogation()
                else:
                    self._serve_404()

            def _serve_main_page(self):
                """Serve the main HTML page."""
                html = self._generate_html()
                self.send_response(200)
                self.send_header("Content - type", "text / html")
                self.end_headers()
                self.wfile.write(html.encode("utf - 8"))

            def _serve_status(self):
                """Serve interrogation status."""
                status = interrogator.get_enhanced_interrogation_status()
                self._send_json_response(status)

            def _serve_questions(self):
                """Serve current questions."""
                questions_data = interrogator.get_current_questions()
                self._send_json_response(questions_data)

            def _serve_project_types(self):
                """Serve available project types."""
                project_types = [
                    {"value": pt.value, "label": pt.value.replace("_", " ").title()}
                    for pt in ProjectType
                ]
                self._send_json_response({"project_types": project_types})

            def _handle_start_interrogation(self):
                """Handle start interrogation request."""
                content_length = int(self.headers["Content - Length"])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode("utf - 8"))

                project_type = ProjectType(data.get("project_type", "generic"))
                result = interrogator.start_enhanced_interrogation(project_type)
                self._send_json_response(result)

            def _handle_submit_response(self):
                """Handle submit response request."""
                content_length = int(self.headers["Content - Length"])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode("utf - 8"))

                phase = data.get("phase")
                question_id = data.get("question_id")
                response = data.get("response")

                result = interrogator.submit_enhanced_response(
                    phase, question_id, response
                )
                self._send_json_response(result)

            def _handle_complete_interrogation(self):
                """Handle complete interrogation request."""
                result = interrogator.force_complete_interrogation()
                self._send_json_response(result)

            def _send_json_response(self, data):
                """Send JSON response."""
                self.send_response(200)
                self.send_header("Content - type", "application / json")
                self.end_headers()
                self.wfile.write(json.dumps(data).encode("utf - 8"))

            def _serve_404(self):
                """Serve 404 error."""
                self.send_response(404)
                self.send_header("Content - type", "text / plain")
                self.end_headers()
                self.wfile.write(b"Not Found")

            def _generate_html(self):
                """Generate the main HTML page."""
                return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF - 8">
    <meta name="viewport" content="width = device - width, initial - scale = 1.0">
    <title > AI Onboard - Vision Interrogation </ title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box - sizing: border - box;
        }

        body {
            font - family: -apple - system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans - serif;
            background: linear - gradient(135deg, #667eea 0%, #764ba2 100%);
            min - height: 100vh;
            padding: 20px;
        }

        .container {
            max - width: 800px;
            margin: 0 auto;
            background: white;
            border - radius: 12px;
            box - shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }

        .header {
            background: linear - gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            color: white;
            padding: 30px;
            text - align: center;
        }

        .header h1 {
            font - size: 2.5rem;
            margin - bottom: 10px;
            font - weight: 700;
        }

        .header p {
            font - size: 1.1rem;
            opacity: 0.9;
        }

        .content {
            padding: 40px;
        }

        .status - card {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border - radius: 8px;
            padding: 20px;
            margin - bottom: 30px;
        }

        .status - card h3 {
            color: #1e293b;
            margin - bottom: 15px;
            font - size: 1.2rem;
        }

        .status - info {
            display: grid;
            grid - template - columns: repeat(auto - fit, minmax(200px, 1fr));
            gap: 15px;
        }

        .status - item {
            display: flex;
            justify - content: space - between;
            padding: 10px 0;
            border - bottom: 1px solid #e2e8f0;
        }

        .status - item:last - child {
            border - bottom: none;
        }

        .status - label {
            font - weight: 500;
            color: #64748b;
        }

        .status - value {
            font - weight: 600;
            color: #1e293b;
        }

        .project - type - selector {
            margin - bottom: 30px;
        }

        .project - type - selector label {
            display: block;
            margin - bottom: 10px;
            font - weight: 600;
            color: #1e293b;
        }

        .project - type - selector select {
            width: 100%;
            padding: 12px;
            border: 1px solid #d1d5db;
            border - radius: 6px;
            font - size: 1rem;
            background: white;
        }

        .button {
            background: linear - gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border - radius: 6px;
            font - size: 1rem;
            font - weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box - shadow 0.2s;
        }

        .button:hover {
            transform: translateY(-2px);
            box - shadow: 0 10px 20px rgba(79, 70, 229, 0.3);
        }

        .button:disabled {
            opacity: 0.5;
            cursor: not - allowed;
            transform: none;
            box - shadow: none;
        }

        .button.secondary {
            background: #6b7280;
        }

        .button.success {
            background: #10b981;
        }

        .questions - section {
            margin - top: 30px;
        }

        .question - card {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border - radius: 8px;
            padding: 20px;
            margin - bottom: 20px;
        }

        .question - text {
            font - size: 1.1rem;
            font - weight: 600;
            color: #1e293b;
            margin - bottom: 15px;
        }

        .question - input {
            width: 100%;
            min - height: 100px;
            padding: 12px;
            border: 1px solid #d1d5db;
            border - radius: 6px;
            font - size: 1rem;
            font - family: inherit;
            resize: vertical;
        }

        .confidence - slider {
            width: 100%;
            margin: 15px 0;
        }

        .confidence - label {
            display: flex;
            justify - content: space - between;
            margin - bottom: 5px;
            font - size: 0.9rem;
            color: #64748b;
        }

        .insights - section {
            background: #ecfdf5;
            border: 1px solid #a7f3d0;
            border - radius: 8px;
            padding: 20px;
            margin - top: 20px;
        }

        .insights - section h4 {
            color: #065f46;
            margin - bottom: 15px;
        }

        .insight - item {
            background: white;
            border: 1px solid #a7f3d0;
            border - radius: 6px;
            padding: 15px;
            margin - bottom: 10px;
        }

        .insight - type {
            font - weight: 600;
            color: #047857;
            margin - bottom: 5px;
        }

        .insight - description {
            color: #065f46;
            margin - bottom: 10px;
        }

        .insight - recommendations {
            font - size: 0.9rem;
            color: #047857;
        }

        .loading {
            text - align: center;
            padding: 40px;
            color: #64748b;
        }

        .error {
            background: #fef2f2;
            border: 1px solid #fecaca;
            color: #dc2626;
            padding: 15px;
            border - radius: 6px;
            margin - bottom: 20px;
        }

        .success {
            background: #f0fdf4;
            border: 1px solid #bbf7d0;
            color: #166534;
            padding: 15px;
            border - radius: 6px;
            margin - bottom: 20px;
        }

        .progress - bar {
            width: 100%;
            height: 8px;
            background: #e2e8f0;
            border - radius: 4px;
            overflow: hidden;
            margin - bottom: 20px;
        }

        .progress - fill {
            height: 100%;
            background: linear - gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            transition: width 0.3s ease;
        }

        @media (max - width: 768px) {
            .container {
                margin: 10px;
                border - radius: 8px;
            }

            .header {
                padding: 20px;
            }

            .header h1 {
                font - size: 2rem;
            }

            .content {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Vision Interrogation </ h1>
            <p > Define your project vision through guided questioning </ p>
        </div>

        <div class="content">
            <div id="status - section" class="status - card">
                <h3 > Current Status </ h3>
                <div id="status - content" class="loading">
                    Loading status...
                </div>
            </div>

            <div id="project - type - section" class="project - type - selector" style="display: none;">
                <label for="project - type">Select Project Type:</label>
                <select id="project - type">
                    <option value="generic">Generic Project </ option>
                    <option value="web_application">Web Application </ option>
                    <option value="mobile_app">Mobile App </ option>
                    <option value="data_science">Data Science </ option>
                    <option value="api_service">API Service </ option>
                    <option value="ai_ml_project">AI / ML Project </ option>
                </select>
                <button id="start - btn" class="button" style="margin - top: 15px;">
                    Start Vision Interrogation
                </button>
            </div>

            <div id="questions - section" class="questions - section" style="display: none;">
                <div id="progress - section">
                    <div class="progress - bar">
                        <div id="progress - fill" class="progress - fill" style="width: 0%"></div>
                    </div>
                    <div id="progress - text">Progress: 0 %</ div>
                </div>

                <div id="current - question"></div>
                <div id="insights - section" class="insights - section" style="display: none;">
                    <h4>💡 Insights & Recommendations </ h4>
                    <div id="insights - content"></div>
                </div>
            </div>

            <div id="completion - section" style="display: none;">
                <div class="success">
                    <h3>🎉 Vision Interrogation Complete !</ h3>
                    <p > Your project vision has been successfully defined. You can now proceed with development.</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        class VisionInterrogationApp {
            constructor() {
                this.currentPhase = null;
                this.currentQuestions = [];
                this.currentQuestionIndex = 0;
                this.projectType = 'generic';
                this.init();
            }

            async init() {
                await this.loadStatus();
                this.setupEventListeners();
            }

            setupEventListeners() {
                document.getElementById('start - btn').addEventListener('click', () => {
                    this.startInterrogation();
                });
            }

            async loadStatus() {
                try {
                    const response = await fetch('/api / status');
                    const status = await response.json();
                    this.updateStatusDisplay(status);
                } catch (error) {
                    console.error('Error loading status:', error);
                    this.showError('Failed to load status');
                }
            }

            updateStatusDisplay(status) {
                const statusContent = document.getElementById('status - content');

                if (status.status === 'no_interrogation') {
                    statusContent.innerHTML = `
                        <div class="status - info">
                            <div class="status - item">
                                <span class="status - label">Status:</span>
                                <span class="status - value">Not Started </ span>
                            </div>
                            <div class="status - item">
                                <span class="status - label">Project Type:</span>
                                <span class="status - value">Not Selected </ span>
                            </div>
                        </div>
                    `;
                    document.getElementById('project - type - section').style.display = 'block';
                } else if (status.status === 'in_progress') {
                    statusContent.innerHTML = `
                        <div class="status - info">
                            <div class="status - item">
                                <span class="status - label">Status:</span>
                                <span class="status - value">In Progress </ span>
                            </div>
                            <div class="status - item">
                                <span class="status - label">Project Type:</span>
                                <span class="status - value">${status.project_type}</span>
                            </div>
                            <div class="status - item">
                                <span class="status - label">Current Phase:</span>
                                <span class="status - value">${status.current_phase}</span>
                            </div>
                            <div class="status - item">
                                <span class="status - label">Vision Quality:</span>
                                <span class="status - value">${(status.vision_quality_score * 100).toFixed(1)}%</span>
                            </div>
                        </div>
                    `;
                    this.loadQuestions();
                } else if (status.status === 'completed') {
                    statusContent.innerHTML = `
                        <div class="status - info">
                            <div class="status - item">
                                <span class="status - label">Status:</span>
                                <span class="status - value">Completed </ span>
                            </div>
                            <div class="status - item">
                                <span class="status - label">Project Type:</span>
                                <span class="status - value">${status.project_type}</span>
                            </div>
                            <div class="status - item">
                                <span class="status - label">Final Quality:</span>
                                <span class="status - value">${(status.vision_quality_score * 100).toFixed(1)}%</span>
                            </div>
                        </div>
                    `;
                    document.getElementById('completion - section').style.display = 'block';
                }
            }

            async startInterrogation() {
                const projectType = document.getElementById('project - type').value;

                try {
                    const response = await fetch('/api / start', {
                        method: 'POST',
                        headers: {
                            'Content - Type': 'application / json',
                        },
                        body: JSON.stringify({ project_type: projectType })
                    });

                    const result = await response.json();

                    if (result.status === 'enhanced_interrogation_started') {
                        this.projectType = projectType;
                        document.getElementById('project - type - section').style.display = 'none';
                        document.getElementById('questions - section').style.display = 'block';
                        await this.loadQuestions();
                    } else {
                        this.showError('Failed to start interrogation: ' + result.message);
                    }
                } catch (error) {
                    console.error('Error starting interrogation:', error);
                    this.showError('Failed to start interrogation');
                }
            }

            async loadQuestions() {
                try {
                    const response = await fetch('/api / questions');
                    const questionsData = await response.json();

                    if (questionsData.status === 'questions_available') {
                        this.currentPhase = questionsData.current_phase;
                        this.currentQuestions = questionsData.questions;
                        this.currentQuestionIndex = 0;
                        this.displayCurrentQuestion();
                        this.updateProgress(questionsData.progress);
                    } else {
                        this.showError('No questions available');
                    }
                } catch (error) {
                    console.error('Error loading questions:', error);
                    this.showError('Failed to load questions');
                }
            }

            displayCurrentQuestion() {
                if (this.currentQuestionIndex >= this.currentQuestions.length) {
                    this.showCompletion();
                    return;
                }

                const question = this.currentQuestions[this.currentQuestionIndex];
                const questionContainer = document.getElementById('current - question');

                questionContainer.innerHTML = `
                    <div class="question - card">
                        <div class="question - text">${question.question}</div>
                        <textarea
                            id="answer - input"
                            class="question - input"
                            placeholder="Enter your answer here..."
                        ></textarea>
                        <div class="confidence - label">
                            <span > Confidence Level </ span>
                            <span id="confidence - value">50 %</ span>
                        </div>
                        <input
                            type="range"
                            id="confidence - slider"
                            class="confidence - slider"
                            min="0"
                            max="100"
                            value="50"
                        >
                        <button id="submit - btn" class="button" style="margin - top: 15px;">
                            Submit Answer
                        </button>
                    </div>
                `;

                // Setup confidence slider
                const slider = document.getElementById('confidence - slider');
                const value = document.getElementById('confidence - value');

                slider.addEventListener('input', (e) => {
                    value.textContent = e.target.value + '%';
                });

                // Setup submit button
                document.getElementById('submit - btn').addEventListener('click', () => {
                    this.submitAnswer(question);
                });
            }

            async submitAnswer(question) {
                const answer = document.getElementById('answer - input').value.trim();
                const confidence = parseInt(document.getElementById('confidence - slider').value) / 100;

                if (!answer) {
                    this.showError('Please enter an answer');
                    return;
                }

                try {
                    const response = await fetch('/api / submit', {
                        method: 'POST',
                        headers: {
                            'Content - Type': 'application / json',
                        },
                        body: JSON.stringify({
                            phase: this.currentPhase,
                            question_id: question.id,
                            response: {
                                answer: answer,
                                confidence: confidence
                            }
                        })
                    });

                    const result = await response.json();

                    if (result.status === 'enhanced_response_accepted') {
                        this.showInsights(result);
                        this.currentQuestionIndex++;

                        if (result.phase_complete) {
                            await this.loadQuestions(); // Load next phase
                        } else {
                            this.displayCurrentQuestion();
                        }

                        await this.loadStatus(); // Update status
                    } else {
                        this.showError('Failed to submit answer: ' + result.message);
                    }
                } catch (error) {
                    console.error('Error submitting answer:', error);
                    this.showError('Failed to submit answer');
                }
            }

            showInsights(result) {
                if (result.recommendations && result.recommendations.length > 0) {
                    const insightsSection = document.getElementById('insights - section');
                    const insightsContent = document.getElementById('insights - content');

                    let insightsHtml = '';
                    result.recommendations.forEach(rec => {
                        insightsHtml += `
                            <div class="insight - item">
                                <div class="insight - description">${rec}</div>
                            </div>
                        `;
                    });

                    insightsContent.innerHTML = insightsHtml;
                    insightsSection.style.display = 'block';
                }
            }

            updateProgress(progress) {
                const progressFill = document.getElementById('progress - fill');
                const progressText = document.getElementById('progress - text');

                progressFill.style.width = progress + '%';
                progressText.textContent = `Progress: ${progress.toFixed(1)}%`;
            }

            showCompletion() {
                document.getElementById('questions - section').style.display = 'none';
                document.getElementById('completion - section').style.display = 'block';
            }

            showError(message) {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'error';
                errorDiv.textContent = message;

                const content = document.querySelector('.content');
                content.insertBefore(errorDiv, content.firstChild);

                setTimeout(() => {
                    errorDiv.remove();
                }, 5000);
            }
        }

        // Initialize the app when the page loads
        document.addEventListener('DOMContentLoaded', () => {
            new VisionInterrogationApp();
        });
    </script>
</body>
</html>
                """

        return VisionRequestHandler


def start_vision_web_interface(root: Path, port: int = 8080) -> Dict[str, Any]:
    """Start the vision interrogation web interface."""
    interface = VisionWebInterface(root, port)
    return interface.start_web_interface()


def stop_vision_web_interface(root: Path) -> Dict[str, Any]:
    """Stop the vision interrogation web interface."""
    # This would need to be implemented with proper server management
    return {"status": "success", "message": "Web interface stopped"}
