# FinanceBot Demo

Giao diện demo nhanh cho FinanceBot Multi-Agent System sử dụng Gradio.

## 🚀 Chạy Demo Nhanh

### Cách 1: Sử dụng script tự động
```bash
cd ui
python run_demo.py
```

### Cách 2: Chạy trực tiếp
```bash
cd ui
python demo.py
```

## 📋 Yêu cầu

1. **Environment Variables:**
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   ```

2. **Dependencies:**
   - Gradio >= 4.0.0
   - Tất cả dependencies từ project chính

## 🌐 Truy cập Demo

Sau khi chạy, demo sẽ có sẵn tại:
- **Local:** http://localhost:7860
- **Network:** http://0.0.0.0:7860

## 🎯 Tính năng Demo

### 1. 💬 Chat với FinanceBot
- Giao diện chat trực tiếp
- Hỗ trợ câu hỏi tự nhiên về tài chính
- Hiển thị thông tin agent được sử dụng

### 2. 📈 Phân tích Cổ phiếu
- Nhập mã cổ phiếu (AAPL, MSFT, TSLA...)
- Chọn loại phân tích (comprehensive, technical, fundamental, sentiment)
- Chọn khung thời gian (1 tháng, 3 tháng, 6 tháng, 1 năm, 2 năm)

### 3. 📊 Tạo Biểu đồ
- Tạo các loại biểu đồ khác nhau
- Hỗ trợ nhiều loại chart (price, candlestick, RSI, MACD...)
- Tùy chọn khung thời gian linh hoạt

## 🔧 Cấu hình

Demo sử dụng cấu hình từ project chính:
- `app/core/config.py` - Cấu hình chung
- `app/services/chat_service.py` - Service xử lý chat
- `src/agents/` - Các agent chuyên biệt

## 🐛 Troubleshooting

### Lỗi "Chat service not initialized"
- Kiểm tra OPENAI_API_KEY đã được set
- Kiểm tra tất cả dependencies đã được cài đặt

### Lỗi Import
- Đảm bảo đang chạy từ thư mục gốc của project
- Kiểm tra PYTHONPATH

### Demo không load
- Kiểm tra port 7860 có bị chiếm không
- Thử port khác: `demo.launch(server_port=7861)`

## 📝 Ghi chú

- Demo này chỉ để test nhanh các tính năng
- Để sử dụng production, hãy sử dụng API server chính
- Tất cả dữ liệu được xử lý real-time qua OpenAI API

