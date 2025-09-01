# GUI Directory Description

## Startup Method

```bash
cd GUI
streamlit run app.py
```

Or run run.py directly from the root directory

## Function Description

### Currently Implemented
- ✅ Basic chat interface framework
- ✅ Left chat window
- ✅ Right background logs
- ✅ Component structure
- ✅ LLM configuration management
- ✅ Responsive layout
- ✅ Actual chat conversation
- ✅ Message sending and receiving
- ✅ Chat history records
- ✅ Logging functionality

### Pending Implementation
- ❌ Complete workflow records
- ❌ Real-time policy status
- ❌ web_search URL references

## Page Layout

### Left Side - Chat Window
- Chat record display area
- Message input box
- Send and clear buttons

### Right Side - Background Logs
- System log display
- Log refresh and export functionality

### Top - Status Information
- Bot status
- Execution cycles
- Single response time
- Total response time

### Sidebar - Configuration Options
- AI model selection
- Model parameter configuration
- Chat settings
- Action buttons

## Technology Stack

- **Frontend Framework**: Streamlit
- **Configuration Management**: python-dotenv
- **Layout**: Responsive grid layout
- **Components**: Modular component design


## Notes

- Ensure `streamlit` and `python-dotenv` are installed
- Environment variable configuration is in the `.env` file in the project root directory
- Components share state through `st.session_state`