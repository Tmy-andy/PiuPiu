// theme-effects.js - Xử lý hiệu ứng đặc biệt cho từng theme

class ThemeEffects {
    constructor() {
        this.currentTheme = 'default';
        this.effectsEnabled = true;
        this.isMobile = window.innerWidth <= 768;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadSavedTheme();
    }

    setupEventListeners() {
        // Theo dõi thay đổi theme
        document.addEventListener('themeChanged', (e) => {
            this.applyTheme(e.detail.theme);
        });

        // Tối ưu hiệu ứng khi thay đổi kích thước màn hình
        window.addEventListener('resize', () => {
            this.isMobile = window.innerWidth <= 768;
            this.updateEffectsForDevice();
        });

        // Tạm dừng hiệu ứng khi tab không active (tiết kiệm pin)
        document.addEventListener('visibilitychange', () => {
            this.effectsEnabled = !document.hidden;
            this.toggleEffects();
        });
    }

    applyTheme(theme) {
        this.currentTheme = theme;
        document.documentElement.setAttribute('data-theme', theme);
        
        // Xóa các hiệu ứng cũ
        this.clearAllEffects();
        
        // Áp dụng hiệu ứng mới
        switch(theme) {
            case 'galaxy':
                this.initGalaxyEffects();
                break;
            case 'sakura':
                this.initSakuraEffects();
                break;
            case 'forest':
                this.initForestEffects();
                break;
            case 'ocean':
                this.initOceanEffects();
                break;
            case 'sunset':
                this.initSunsetEffects();
                break;
            default:
                break;
        }
        
        // Lưu theme đã chọn
        localStorage.setItem('selectedTheme', theme);
        
        // Trigger custom event
        document.dispatchEvent(new CustomEvent('themeApplied', {
            detail: { theme: theme }
        }));
    }

    // ============= GALAXY EFFECTS =============
    initGalaxyEffects() {
        this.createGalaxyCursor();
        this.createShootingStars();
        this.initGalaxyInteraction();
    }

    createGalaxyCursor() {
        const cursor = document.createElement('div');
        cursor.className = 'galaxy-cursor';
        cursor.id = 'galaxyCursor';
        document.body.appendChild(cursor);

        let mouseX = 0, mouseY = 0;
        let cursorX = 0, cursorY = 0;

        const updateCursor = () => {
            cursorX += (mouseX - cursorX) * 0.1;
            cursorY += (mouseY - cursorY) * 0.1;
            
            cursor.style.left = cursorX - 10 + 'px';
            cursor.style.top = cursorY - 10 + 'px';
            
            if (this.effectsEnabled) {
                requestAnimationFrame(updateCursor);
            }
        };

        const onMouseMove = (e) => {
            mouseX = e.clientX;
            mouseY = e.clientY;
            cursor.style.opacity = '1';
        };

        const onMouseLeave = () => {
            cursor.style.opacity = '0';
        };

        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseleave', onMouseLeave);
        
        if (this.effectsEnabled) {
            requestAnimationFrame(updateCursor);
        }
    }

    createShootingStars() {
        const createStar = () => {
            if (!this.effectsEnabled || this.currentTheme !== 'galaxy') return;
            
            const star = document.createElement('div');
            star.className = 'shooting-star';
            star.style.left = Math.random() * 100 + 'vw';
            star.style.top = Math.random() * 100 + 'vh';
            star.style.animationDelay = Math.random() * 3 + 's';
            document.body.appendChild(star);

            setTimeout(() => {
                if (star.parentNode) {
                    star.remove();
                }
            }, 3000);
        };

        const starInterval = setInterval(() => {
            if (this.currentTheme === 'galaxy' && this.effectsEnabled) {
                createStar();
            } else if (this.currentTheme !== 'galaxy') {
                clearInterval(starInterval);
            }
        }, this.isMobile ? 3000 : 2000);
    }

    initGalaxyInteraction() {
        const createParticle = (x, y) => {
            const particle = document.createElement('div');
            particle.style.cssText = `
                position: fixed;
                width: 4px;
                height: 4px;
                background: rgba(139, 92, 246, 0.8);
                border-radius: 50%;
                pointer-events: none;
                z-index: 9998;
                left: ${x}px;
                top: ${y}px;
                animation: particleFloat 1s ease-out forwards;
            `;
            document.body.appendChild(particle);

            setTimeout(() => particle.remove(), 1000);
        };

        // Thêm CSS animation cho particle
        if (!document.getElementById('galaxy-particle-style')) {
            const style = document.createElement('style');
            style.id = 'galaxy-particle-style';
            style.textContent = `
                @keyframes particleFloat {
                    0% { transform: scale(0) translateY(0); opacity: 1; }
                    100% { transform: scale(1) translateY(-50px); opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        }

        document.addEventListener('click', (e) => {
            if (this.currentTheme === 'galaxy' && this.effectsEnabled) {
                for (let i = 0; i < 5; i++) {
                    setTimeout(() => {
                        createParticle(
                            e.clientX + (Math.random() - 0.5) * 20,
                            e.clientY + (Math.random() - 0.5) * 20
                        );
                    }, i * 100);
                }
            }
        });
    }

    // ============= SAKURA EFFECTS =============
    initSakuraEffects() {
        this.createSakuraPetals();
    }

    createSakuraPetals() {
        const createPetal = () => {
            if (!this.effectsEnabled || this.currentTheme !== 'sakura') return;
            
            const petal = document.createElement('div');
            petal.className = 'sakura-petal';
            petal.style.left = Math.random() * 100 + 'vw';
            petal.style.animationDelay = Math.random() * 2 + 's';
            petal.style.animationDuration = (6 + Math.random() * 4) + 's';
            document.body.appendChild(petal);

            setTimeout(() => {
                if (petal.parentNode) {
                    petal.remove();
                }
            }, 10000);
        };

        const petalInterval = setInterval(() => {
            if (this.currentTheme === 'sakura' && this.effectsEnabled) {
                createPetal();
            } else if (this.currentTheme !== 'sakura') {
                clearInterval(petalInterval);
            }
        }, this.isMobile ? 2000 : 1500);
    }

    // ============= FOREST EFFECTS =============
    initForestEffects() {
        this.createForestLeaves();
    }

    createForestLeaves() {
        const createLeaf = () => {
            if (!this.effectsEnabled || this.currentTheme !== 'forest') return;
            
            const leaf = document.createElement('div');
            leaf.className = 'forest-leaf';
            leaf.style.left = Math.random() * 100 + 'vw';
            leaf.style.animationDelay = Math.random() * 3 + 's';
            leaf.style.animationDuration = (8 + Math.random() * 4) + 's';
            document.body.appendChild(leaf);

            setTimeout(() => {
                if (leaf.parentNode) {
                    leaf.remove();
                }
            }, 12000);
        };

        const leafInterval = setInterval(() => {
            if (this.currentTheme === 'forest' && this.effectsEnabled) {
                createLeaf();
            } else if (this.currentTheme !== 'forest') {
                clearInterval(leafInterval);
            }
        }, this.isMobile ? 3000 : 2500);
    }

    // ============= OCEAN EFFECTS =============
    initOceanEffects() {
        this.createOceanBubbles();
    }

    createOceanBubbles() {
        const createBubble = () => {
            if (!this.effectsEnabled || this.currentTheme !== 'ocean') return;
            
            const bubble = document.createElement('div');
            bubble.style.cssText = `
                position: fixed;
                width: ${4 + Math.random() * 8}px;
                height: ${4 + Math.random() * 8}px;
                background: rgba(14, 165, 233, 0.3);
                border-radius: 50%;
                bottom:-10px;
                left: ${Math.random() * 100}vw;
                pointer-events: none;
                z-index: -1;
                animation: bubbleRise ${8 + Math.random() * 4}s linear infinite;
                opacity: 0.6;
            `;
            document.body.appendChild(bubble);

            setTimeout(() => {
                if (bubble.parentNode) {
                    bubble.remove();
                }
            }, 12000);
        };

        // Thêm CSS animation cho bubble
        if (!document.getElementById('ocean-bubble-style')) {
            const style = document.createElement('style');
            style.id = 'ocean-bubble-style';
            style.textContent = `
                @keyframes bubbleRise {
                    0% {
                        transform: translateY(100vh) scale(0);
                        opacity: 0;
                    }
                    10% {
                        opacity: 0.6;
                        transform: translateY(90vh) scale(1);
                    }
                    90% {
                        opacity: 0.6;
                    }
                    100% {
                        transform: translateY(-100px) scale(0);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }

        const bubbleInterval = setInterval(() => {
            if (this.currentTheme === 'ocean' && this.effectsEnabled) {
                createBubble();
            } else if (this.currentTheme !== 'ocean') {
                clearInterval(bubbleInterval);
            }
        }, this.isMobile ? 4000 : 3000);
    }

    // ============= SUNSET EFFECTS =============
    initSunsetEffects() {
        this.createSunsetGlow();
        this.createFloatingEmbers();
    }

    createSunsetGlow() {
        const glow = document.createElement('div');
        glow.className = 'sunset-glow';
        glow.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: radial-gradient(circle at 70% 20%, rgba(255, 107, 107, 0.1) 0%, transparent 50%);
            pointer-events: none;
            z-index: -1;
            animation: sunsetGlow 20s ease-in-out infinite;
        `;
        document.body.appendChild(glow);

        // Thêm CSS animation cho sunset glow
        if (!document.getElementById('sunset-glow-style')) {
            const style = document.createElement('style');
            style.id = 'sunset-glow-style';
            style.textContent = `
                @keyframes sunsetGlow {
                    0%, 100% { opacity: 0.3; }
                    50% { opacity: 0.8; }
                }
            `;
            document.head.appendChild(style);
        }
    }

    createFloatingEmbers() {
        const createEmber = () => {
            if (!this.effectsEnabled || this.currentTheme !== 'sunset') return;
            
            const ember = document.createElement('div');
            ember.style.cssText = `
                position: fixed;
                width: ${3 + Math.random() * 6}px;
                height: ${3 + Math.random() * 6}px;
                background: radial-gradient(circle, #ff6b6b 0%, #f97316 100%);
                border-radius: 50%;
                bottom: -10px;
                left: ${Math.random() * 100}vw;
                pointer-events: none;
                z-index: -1;
                animation: emberFloat ${15 + Math.random() * 10}s linear infinite;
                opacity: 0.7;
                box-shadow: 0 0 10px rgba(255, 107, 107, 0.5);
            `;
            document.body.appendChild(ember);

            setTimeout(() => {
                if (ember.parentNode) {
                    ember.remove();
                }
            }, 25000);
        };

        // Thêm CSS animation cho ember
        if (!document.getElementById('sunset-ember-style')) {
            const style = document.createElement('style');
            style.id = 'sunset-ember-style';
            style.textContent = `
                @keyframes emberFloat {
                    0% {
                        transform: translateY(100vh) translateX(0) rotate(0deg);
                        opacity: 0;
                    }
                    10% {
                        opacity: 0.7;
                    }
                    50% {
                        transform: translateY(50vh) translateX(20px) rotate(180deg);
                    }
                    90% {
                        opacity: 0.7;
                    }
                    100% {
                        transform: translateY(-100px) translateX(-20px) rotate(360deg);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }

        const emberInterval = setInterval(() => {
            if (this.currentTheme === 'sunset' && this.effectsEnabled) {
                createEmber();
            } else if (this.currentTheme !== 'sunset') {
                clearInterval(emberInterval);
            }
        }, this.isMobile ? 5000 : 3500);
    }

    // ============= UTILITY METHODS =============
    clearAllEffects() {
        // Xóa tất cả hiệu ứng cũ
        const effectElements = [
            '#galaxyCursor',
            '.shooting-star',
            '.sakura-petal',
            '.forest-leaf',
            '.sunset-glow'
        ];

        effectElements.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(el => el.remove());
        });

        // Xóa event listeners cũ
        document.removeEventListener('mousemove', this.onMouseMove);
        document.removeEventListener('mouseleave', this.onMouseLeave);
        document.removeEventListener('click', this.onClickEffect);
    }

    toggleEffects() {
        const body = document.body;
        if (this.effectsEnabled) {
            body.classList.remove('effects-paused');
            this.applyTheme(this.currentTheme);
        } else {
            body.classList.add('effects-paused');
            // Tạm dừng tất cả animation
            const style = document.createElement('style');
            style.id = 'pause-effects';
            style.textContent = `
                .effects-paused * {
                    animation-play-state: paused !important;
                }
            `;
            document.head.appendChild(style);
        }
    }

    updateEffectsForDevice() {
        // Tối ưu hiệu ứng cho mobile
        if (this.isMobile) {
            // Giảm số lượng hiệu ứng trên mobile
            const mobileOptimizations = {
                galaxy: { starFrequency: 3000, particleCount: 3 },
                sakura: { petalFrequency: 2500, petalCount: 1 },
                forest: { leafFrequency: 4000, leafCount: 1 },
                ocean: { bubbleFrequency: 5000, bubbleCount: 1 },
                sunset: { emberFrequency: 6000, emberCount: 1 }
            };
            
            this.mobileConfig = mobileOptimizations;
        }
    }

    loadSavedTheme() {
        const savedTheme = localStorage.getItem('selectedTheme');
        if (savedTheme) {
            this.applyTheme(savedTheme);
        }
    }

    // ============= PERFORMANCE MONITORING =============
    monitorPerformance() {
        if (performance.memory) {
            const memoryUsage = performance.memory.usedJSHeapSize / 1024 / 1024;
            if (memoryUsage > 100) { // 100MB
                console.warn('High memory usage detected, reducing effects');
                this.reduceEffects();
            }
        }
    }

    reduceEffects() {
        // Giảm hiệu ứng khi phát hiện hiệu năng kém
        this.effectsEnabled = false;
        setTimeout(() => {
            this.effectsEnabled = true;
        }, 5000);
    }

    // ============= THEME SWITCHING ANIMATION =============
    animateThemeSwitch(fromTheme, toTheme) {
        const overlay = document.createElement('div');
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: black;
            z-index: 10000;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
        `;
        document.body.appendChild(overlay);

        // Fade out
        setTimeout(() => {
            overlay.style.opacity = '1';
        }, 10);

        // Switch theme
        setTimeout(() => {
            this.applyTheme(toTheme);
        }, 150);

        // Fade in
        setTimeout(() => {
            overlay.style.opacity = '0';
            setTimeout(() => {
                overlay.remove();
            }, 300);
        }, 300);
    }

    // ============= ACCESSIBILITY =============
    handleAccessibility() {
        // Kiểm tra prefer-reduced-motion
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            this.effectsEnabled = false;
            console.log('Reduced motion preference detected, effects disabled');
        }

        // Tắt hiệu ứng khi battery thấp
        if ('getBattery' in navigator) {
            navigator.getBattery().then(battery => {
                if (battery.level < 0.2) {
                    this.effectsEnabled = false;
                    console.log('Low battery detected, effects disabled');
                }
            });
        }
    }

    // ============= CLEANUP =============
    destroy() {
        this.clearAllEffects();
        this.effectsEnabled = false;
        
        // Xóa event listeners
        document.removeEventListener('themeChanged', this.onThemeChanged);
        window.removeEventListener('resize', this.onResize);
        document.removeEventListener('visibilitychange', this.onVisibilityChange);
        
        // Xóa style elements
        const styleElements = [
            '#galaxy-particle-style',
            '#ocean-bubble-style',
            '#sunset-glow-style',
            '#sunset-ember-style',
            '#pause-effects'
        ];
        
        styleElements.forEach(id => {
            const element = document.getElementById(id);
            if (element) element.remove();
        });
    }
}

// ============= INITIALIZATION =============
document.addEventListener('DOMContentLoaded', () => {
    window.themeEffects = new ThemeEffects();
    
    // Expose methods globally for theme selector
    window.changeTheme = (theme) => {
        window.themeEffects.applyTheme(theme);
    };
    
    // Performance monitoring
    setInterval(() => {
        window.themeEffects.monitorPerformance();
    }, 30000); // Check every 30 seconds
});

// ============= EXPORT FOR MODULE SYSTEMS =============
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeEffects;
}

// ============= THEME PRESETS =============
const THEME_PRESETS = {
    default: {
        name: 'Mặc định',
        description: 'Theme cơ bản với màu xanh tím',
        effects: false
    },
    dark: {
        name: 'Tối',
        description: 'Theme tối bảo vệ mắt',
        effects: false
    },
    sakura: {
        name: 'Hoa anh đào',
        description: 'Theme hồng với cánh hoa rơi',
        effects: true
    },
    galaxy: {
        name: 'Thiên hà',
        description: 'Theme vũ trụ với sao băng',
        effects: true
    },
    ocean: {
        name: 'Đại dương',
        description: 'Theme xanh với bong bóng',
        effects: true
    },
    forest: {
        name: 'Rừng xanh',
        description: 'Theme xanh với lá rơi',
        effects: true
    },
    sunset: {
        name: 'Hoàng hôn',
        description: 'Theme cam với hiệu ứng ánh sáng',
        effects: true
    }
};

// Make presets globally available
window.THEME_PRESETS = THEME_PRESETS;