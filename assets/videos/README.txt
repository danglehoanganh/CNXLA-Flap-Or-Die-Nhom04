# HƯỚNG DẪN VIDEO CAMPAIGN MODE 🎥

## Cách thêm video giới thiệu Campaign:
1. **Tải video ngắn**: 5-10 giây, định dạng MP4 (khuyến nghị 400x600px hoặc tự resize).
   - Gợi ý: Animation Flappy Bird intro, "Chào mừng Campaign!", hiệu ứng level.
   - Công cụ cắt: mp3cut.net hoặc CapCut.

2. **Đặt file**: `assets/videos/intro_campaign.mp4`
   - Tạo thư mục `assets/videos/` nếu chưa có (tự động).

3. **Cách hoạt động**:
   - Nhấn **1** trong menu → Video phát fullscreen (overlay đen).
   - **ESC** hoặc **Enter** để skip sớm.
   - Video hết → Tự vào game Campaign mode.
   - Không có file → Skip tự động, console báo "Không tìm video".

4. **Tùy chỉnh trong game.py**:
   ```python
   VIDEO_PATH = "assets/videos/intro_campaign.mp4"  # Đổi tên/path ở đây
   ```

5. **Yêu cầu**:
   - OpenCV (đã có).
   - Video <50MB, ngắn để load nhanh.

**Thêm video → Game pro hơn! 🚀**
**Ví dụ video**: Tìm "flappy bird intro animation" trên YouTube → Download MP4.
