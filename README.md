# 🌌 CosmosQuest: Turn Any Topic into a Learning Adventure

CosmosQuest is an AI-powered educational web application that transforms any topic into an engaging 5-part interactive learning quest. Whether you're exploring "Photosynthesis", "World War II", or "Operating System Deadlocks", CosmosQuest creates a space-themed learning journey with progressively deeper content, mini-quizzes, visual aids, fun facts, and additional resources.

## ✨ Features

- 🚀 **Interactive Learning Quests**: Convert any topic into a structured 5-part learning journey
- 🧠 **AI-Powered Content Generation**: Utilizes Groq API with LLaMA 3.3 70B model for intelligent content creation
- 🎯 **Progressive Learning**: Each quest part builds upon the previous with increasing complexity
- 🎮 **Gamified Experience**: Space-themed interface makes learning feel like an adventure
- 📊 **Mini-Quizzes**: Interactive quizzes to test understanding at each stage
- 🔗 **Additional Resources**: Curated links and materials for deeper exploration
- 📱 **Responsive Design**: Works seamlessly on desktop and mobile devices

## 🛠️ Tech Stack

- **Frontend**: HTML5, Tailwind CSS, JavaScript
- **Backend**: Python Flask
- **AI Model**: Groq API (LLaMA 3.3 70B Versatile)
- **Web Search**: SerperAPI for real-time context
- **Deployment**: Render-ready with production configuration

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Groq API key
- SerperAPI key (optional, for enhanced content)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/questifyai.git
   cd questifyai
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY_1=your_first_groq_api_key
   GROQ_API_KEY_2=your_second_groq_api_key
   GROQ_API_KEY_3=your_third_groq_api_key
   GROQ_API_KEY_4=your_fourth_groq_api_key
   SERPER_API_KEY=your_serper_api_key
   SESSION_SECRET=your_session_secret_key
   FLASK_DEBUG=False
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000`

## 🔧 Configuration

### API Key Management

CosmosQuest features intelligent API key rotation and management:

- **Smart Fallback**: Automatically switches between API keys when rate limits are hit
- **Load Distribution**: Spreads requests across multiple keys
- **Error Recovery**: Handles rate limits with exponential backoff
- **Real-time Monitoring**: Track API usage at `/admin/api-dashboard`

### Quest Configuration

Customize quest generation in `config.py`:

- **Models**: Different AI models for different quest types
- **Temperature**: Control creativity vs consistency
- **Token Limits**: Adjust response length
- **Timeouts**: Configure retry and cooldown periods

## 📁 Project Structure

```
questifyai/
├── app.py                 # Main Flask application
├── routes.py             # URL routes and handlers
├── config.py             # Configuration settings
├── groq_api_manager.py   # API key management and rotation
├── api_service.py        # External API integrations
├── requirements.txt      # Python dependencies
├── static/
│   ├── css/
│   │   └── style.css     # Tailwind CSS styles
│   └── js/
│       ├── app.js        # Main JavaScript functionality
│       └── quest.js      # Quest-specific interactions
├── templates/
│   ├── index.html        # Home page
│   └── quest.html        # Quest display page
└── tests/
    ├── test_api_manager.py
    └── test_integration.py
```

## 🎮 How to Use

1. **Enter a Topic**: Type any subject you want to learn about
2. **Choose Quest Type**: Select from available learning formats
3. **Start Your Journey**: Navigate through 5 progressive learning stages
4. **Take Quizzes**: Test your knowledge with interactive mini-quizzes
5. **Explore Resources**: Access additional materials for deeper learning

## 🚀 Deployment

### Deploy to Render

1. Fork this repository to your GitHub account
2. Connect your GitHub account to Render
3. Create a new Web Service on Render
4. Set environment variables in Render dashboard
5. Deploy automatically from your main branch

### Environment Variables for Production

```env
GROQ_API_KEY_1=your_production_groq_key_1
GROQ_API_KEY_2=your_production_groq_key_2
GROQ_API_KEY_3=your_production_groq_key_3
GROQ_API_KEY_4=your_production_groq_key_4
SERPER_API_KEY=your_production_serper_key
SESSION_SECRET=your_production_session_secret
FLASK_DEBUG=False
```

## 🔍 API Endpoints

- `GET /` - Home page
- `POST /generate-quest` - Generate a new learning quest
- `GET /quest/<quest_id>` - View a specific quest
- `GET /api/status` - API health and status monitoring
- `GET /admin/api-dashboard` - Admin dashboard for API monitoring

## 🧪 Testing

Run the test suite:

```bash
python -m pytest tests/
```

Run specific tests:

```bash
python test_api_manager.py
python test_integration.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/questifyai/issues) page
2. Create a new issue with detailed information
3. Contact the maintainers

## 🙏 Acknowledgments

- Groq for providing the AI API
- Tailwind CSS for the styling framework
- The open-source community for inspiration and tools

---

**Made with ❤️ for learners everywhere**
