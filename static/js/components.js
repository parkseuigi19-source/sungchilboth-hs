/**
 * 성취봇-HS 공통 컴포넌트 및 유틸리티
 */

// ========== 토스트 알림 ==========
const Toast = {
    container: null,

    init() {
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.className = 'toast-container';
            document.body.appendChild(this.container);
        }
    },

    show(message, type = 'info', duration = 3000) {
        this.init();

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;

        const icon = this.getIcon(type);
        toast.innerHTML = `
      <span style="font-size: 1.5rem;">${icon}</span>
      <span>${message}</span>
    `;

        this.container.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideIn 0.3s ease reverse';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    },

    getIcon(type) {
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        return icons[type] || icons.info;
    },

    success(message, duration) {
        this.show(message, 'success', duration);
    },

    error(message, duration) {
        this.show(message, 'error', duration);
    },

    warning(message, duration) {
        this.show(message, 'warning', duration);
    },

    info(message, duration) {
        this.show(message, 'info', duration);
    }
};

// ========== 모달 관리 ==========
const Modal = {
    create(title, content, options = {}) {
        const overlay = document.createElement('div');
        overlay.className = 'modal-overlay';

        const modal = document.createElement('div');
        modal.className = 'modal';

        modal.innerHTML = `
      <div class="modal-header">
        <h3>${title}</h3>
        <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">×</button>
      </div>
      <div class="modal-body">
        ${content}
      </div>
      ${options.footer ? `<div class="modal-footer">${options.footer}</div>` : ''}
    `;

        overlay.appendChild(modal);
        document.body.appendChild(overlay);

        // 애니메이션을 위한 지연
        setTimeout(() => overlay.classList.add('active'), 10);

        // 오버레이 클릭 시 닫기
        if (options.closeOnOverlay !== false) {
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) {
                    this.close(overlay);
                }
            });
        }

        return overlay;
    },

    close(overlay) {
        overlay.classList.remove('active');
        setTimeout(() => overlay.remove(), 300);
    },

    confirm(title, message, onConfirm) {
        const footer = `
      <div style="display: flex; gap: 10px; justify-content: flex-end;">
        <button class="btn btn-ghost" onclick="this.closest('.modal-overlay').remove()">취소</button>
        <button class="btn btn-primary" id="confirmBtn">확인</button>
      </div>
    `;

        const modal = this.create(title, `<p>${message}</p>`, { footer });

        modal.querySelector('#confirmBtn').addEventListener('click', () => {
            onConfirm();
            this.close(modal);
        });
    }
};

// ========== 로딩 오버레이 ==========
const Loading = {
    overlay: null,

    show(message = '로딩 중...') {
        if (this.overlay) return;

        this.overlay = document.createElement('div');
        this.overlay.className = 'loading-overlay';
        this.overlay.innerHTML = `
      <div style="text-align: center;">
        <div class="spinner"></div>
        <p style="margin-top: 16px; color: var(--text-medium);">${message}</p>
      </div>
    `;

        document.body.appendChild(this.overlay);
    },

    hide() {
        if (this.overlay) {
            this.overlay.remove();
            this.overlay = null;
        }
    }
};

// ========== API 호출 헬퍼 ==========
const API = {
    async request(url, options = {}) {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || '요청 실패');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    get(url, options = {}) {
        return this.request(url, { ...options, method: 'GET' });
    },

    post(url, body, options = {}) {
        return this.request(url, {
            ...options,
            method: 'POST',
            body: JSON.stringify(body)
        });
    },

    put(url, body, options = {}) {
        return this.request(url, {
            ...options,
            method: 'PUT',
            body: JSON.stringify(body)
        });
    },

    delete(url, options = {}) {
        return this.request(url, { ...options, method: 'DELETE' });
    }
};

// ========== 차트 렌더링 (Chart.js 사용) ==========
const ChartHelper = {
    // 원형 차트
    createDoughnut(canvas, data, options = {}) {
        return new Chart(canvas, {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values,
                    backgroundColor: data.colors || [
                        '#f58bb3',
                        '#a88bff',
                        '#7dc4ff',
                        '#4caf50',
                        '#ff9800'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                },
                ...options
            }
        });
    },

    // 막대 차트
    createBar(canvas, data, options = {}) {
        return new Chart(canvas, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: data.label || '점수',
                    data: data.values,
                    backgroundColor: '#a88bff',
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                },
                ...options
            }
        });
    },

    // 선 차트
    createLine(canvas, data, options = {}) {
        return new Chart(canvas, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: data.label || '추이',
                    data: data.values,
                    borderColor: '#a88bff',
                    backgroundColor: 'rgba(168, 139, 255, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                ...options
            }
        });
    },

    // 레이더 차트
    createRadar(canvas, data, options = {}) {
        return new Chart(canvas, {
            type: 'radar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: data.label || '성취도',
                    data: data.values,
                    backgroundColor: 'rgba(168, 139, 255, 0.2)',
                    borderColor: '#a88bff',
                    pointBackgroundColor: '#a88bff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100
                    }
                },
                ...options
            }
        });
    }
};

// ========== 유틸리티 함수 ==========
const Utils = {
    // 날짜 포맷팅
    formatDate(dateString) {
        const date = new Date(dateString);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    },

    // 시간 포맷팅
    formatDateTime(dateString) {
        const date = new Date(dateString);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        return `${year}-${month}-${day} ${hours}:${minutes}`;
    },

    // 상대 시간
    timeAgo(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diff = now - date;

        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (days > 0) return `${days}일 전`;
        if (hours > 0) return `${hours}시간 전`;
        if (minutes > 0) return `${minutes}분 전`;
        return '방금 전';
    },

    // 숫자 포맷팅
    formatNumber(num, decimals = 0) {
        return Number(num).toFixed(decimals);
    },

    // 퍼센트 계산
    toPercent(value, total) {
        return ((value / total) * 100).toFixed(1);
    },

    // 로컬 스토리지
    storage: {
        get(key) {
            try {
                const item = localStorage.getItem(key);
                return item ? JSON.parse(item) : null;
            } catch {
                return localStorage.getItem(key);
            }
        },

        set(key, value) {
            const item = typeof value === 'string' ? value : JSON.stringify(value);
            localStorage.setItem(key, item);
        },

        remove(key) {
            localStorage.removeItem(key);
        },

        clear() {
            localStorage.clear();
        }
    },

    // 현재 사용자 정보
    getCurrentUser() {
        return {
            username: localStorage.getItem('user'),
            role: localStorage.getItem('role')
        };
    },

    // 로그아웃
    logout() {
        localStorage.removeItem('user');
        localStorage.removeItem('role');
        window.location.href = '/login';
    },

    // 권한 확인
    checkAuth(requiredRole) {
        const user = this.getCurrentUser();
        if (!user.username) {
            window.location.href = '/login';
            return false;
        }
        if (requiredRole && user.role !== requiredRole) {
            Toast.error('권한이 없습니다');
            return false;
        }
        return true;
    }
};

// ========== 페이지네이션 ==========
const Pagination = {
    create(container, totalItems, itemsPerPage, currentPage, onPageChange) {
        const totalPages = Math.ceil(totalItems / itemsPerPage);

        container.innerHTML = '';

        if (totalPages <= 1) return;

        const nav = document.createElement('nav');
        nav.className = 'pagination';
        nav.style.cssText = 'display: flex; justify-content: center; gap: 8px; margin-top: 24px;';

        // 이전 버튼
        if (currentPage > 1) {
            const prev = this.createButton('‹', () => onPageChange(currentPage - 1));
            nav.appendChild(prev);
        }

        // 페이지 번호
        for (let i = 1; i <= totalPages; i++) {
            if (
                i === 1 ||
                i === totalPages ||
                (i >= currentPage - 2 && i <= currentPage + 2)
            ) {
                const btn = this.createButton(i, () => onPageChange(i), i === currentPage);
                nav.appendChild(btn);
            } else if (i === currentPage - 3 || i === currentPage + 3) {
                const dots = document.createElement('span');
                dots.textContent = '...';
                dots.style.padding = '8px';
                nav.appendChild(dots);
            }
        }

        // 다음 버튼
        if (currentPage < totalPages) {
            const next = this.createButton('›', () => onPageChange(currentPage + 1));
            nav.appendChild(next);
        }

        container.appendChild(nav);
    },

    createButton(text, onClick, active = false) {
        const btn = document.createElement('button');
        btn.textContent = text;
        btn.className = active ? 'btn btn-primary btn-sm' : 'btn btn-ghost btn-sm';
        btn.onclick = onClick;
        return btn;
    }
};

// ========== 전역 객체로 내보내기 ==========
window.Toast = Toast;
window.Modal = Modal;
window.Loading = Loading;
window.API = API;
window.ChartHelper = ChartHelper;
window.Utils = Utils;
window.Pagination = Pagination;
