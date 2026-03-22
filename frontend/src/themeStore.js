import { ref, watch } from 'vue';

// Đọc theme đã lưu ngay lập tức (trước khi Vue mount)
const savedTheme = localStorage.getItem('app_theme') || 'light';

// Khởi tạo trạng thái theme toàn cục
export const globalThemeState = ref(savedTheme);

// Áp dụng theme vào DOM
export const applyThemeToDOM = (theme) => {
    if (theme === 'dark') {
        document.body.classList.add('dark-theme');
        document.body.style.background = '#121212';
    } else {
        document.body.classList.remove('dark-theme');
        document.body.style.background = '';
    }
};

// ✅ Áp dụng ngay khi load module — TRƯỚC khi Vue mount component
// Tránh hiện tượng "nháy sáng" (flash) khi refresh trang
applyThemeToDOM(savedTheme);

// Lắng nghe thay đổi theme — đồng bộ DOM và localStorage
watch(globalThemeState, (newTheme) => {
    localStorage.setItem('app_theme', newTheme);
    applyThemeToDOM(newTheme);
});
