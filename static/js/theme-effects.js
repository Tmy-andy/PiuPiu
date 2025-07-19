// theme-effects.js - Xử lý hiệu ứng đặc biệt cho từng theme

class ThemeEffects {
    constructor() {
        this.currentTheme = 'default';
        this.effectsEnabled = true;
        this.isMobile = window.innerWidth <= 768;
        this.intervals = new Map(); // Lưu trữ các interval để cleanup
        this.animationFrames = new Map(); // Lưu trữ animation frames
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.handleAccessibility();
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
        cursor.style.cssText = `
            position: fixed;
            width: 20px;
            height: 20px;
            background: radial-gradient(circle, rgba(139, 92, 246, 0.8) 0%, transparent 70%);
            border-radius: 50%;
            pointer-events: none;
            z-index: 9999;
            transition: opacity 0.3s ease;
            opacity: 0;
        `;
        document.body.appendChild(cursor);

        let mouseX = 0, mouseY = 0;
        let cursorX = 0, cursorY = 0;

        const updateCursor = () => {
            if (this.currentTheme !== 'galaxy' || !this.effectsEnabled) return;
            
            cursorX += (mouseX - cursorX) * 0.1;
            cursorY += (mouseY - cursorY) * 0.1;
            
            cursor.style.left = cursorX - 10 + 'px';
            cursor.style.top = cursorY - 10 + 'px';
            
            this.animationFrames.set('galaxyCursor', requestAnimationFrame(updateCursor));
        };

        const onMouseMove = (e) => {
            if (this.currentTheme !== 'galaxy') return;
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
            this.animationFrames.set('galaxyCursor', requestAnimationFrame(updateCursor));
        }
    }

    createShootingStars() {
        // Thêm CSS cho shooting stars
        if (!document.getElementById('shooting-star-style')) {
            const style = document.createElement('style');
            style.id = 'shooting-star-style';
            style.textContent = `
                .shooting-star {
                    position: fixed;
                    width: 3px;
                    height: 3px;
                    background: white;
                    border-radius: 50%;
                    z-index: -1;
                    animation: shootingStar 3s linear forwards;
                    box-shadow: 0 0 10px rgba(255, 255, 255, 0.8);
                }
                @keyframes shootingStar {
                    0% {
                        transform: translateX(0) translateY(0) scale(0);
                        opacity: 1;
                    }
                    10% {
                        transform: translateX(-20px) translateY(20px) scale(1);
                        opacity: 1;
                    }
                    100% {
                        transform: translateX(-200px) translateY(200px) scale(0);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }

        const createStar = () => {
            if (!this.effectsEnabled || this.currentTheme !== 'galaxy') return;
            
            const star = document.createElement('div');
            star.className = 'shooting-star';
            star.style.left = Math.random() * window.innerWidth + 'px';
            star.style.top = Math.random() * (window.innerHeight * 0.3) + 'px';
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
                this.intervals.delete('galaxyStars');
            }
        }, this.isMobile ? 3000 : 2000);
        
        this.intervals.set('galaxyStars', starInterval);
    }

    initGalaxyInteraction() {
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

        const clickHandler = (e) => {
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
        };

        document.addEventListener('click', clickHandler);
    }

    // ============= SAKURA EFFECTS =============
    initSakuraEffects() {
        this.createSakuraPetals();
    }

    createSakuraPetals() {
        // Thêm CSS cho sakura petals
        if (!document.getElementById('sakura-petal-style')) {
            const style = document.createElement('style');
            style.id = 'sakura-petal-style';
            style.textContent = `
                .sakura-petal {
                    position: fixed;
                    width: 12px;
                    height: 12px;
                    background: linear-gradient(45deg, #ffc0cb, #ffb6c1);
                    border-radius: 50% 0 50% 0;
                    z-index: -1;
                    animation: sakuraPetalFall 6s linear infinite;
                }
                @keyframes sakuraPetalFall {
                    0% {
                        transform: translateY(-100px) rotate(0deg);
                        opacity: 0;
                    }
                    10% {
                        opacity: 1;
                    }
                    90% {
                        opacity: 1;
                    }
                    100% {
                        transform: translateY(100vh) rotate(360deg);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }

        const createPetal = () => {
            if (!this.effectsEnabled || this.currentTheme !== 'sakura') return;
            
            const petal = document.createElement('div');
            petal.className = 'sakura-petal';
            petal.style.left = Math.random() * window.innerWidth + 'px';
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
                this.intervals.delete('sakuraPetals');
            }
        }, this.isMobile ? 2000 : 1500);
        
        this.intervals.set('sakuraPetals', petalInterval);
    }

    // ============= FOREST EFFECTS =============
    initForestEffects() {
        this.createForestLeaves();
    }

    createForestLeaves() {
        // Thêm CSS cho forest leaves
        if (!document.getElementById('forest-leaf-style')) {
            const style = document.createElement('style');
            style.id = 'forest-leaf-style';
            style.textContent = `
                .forest-leaf {
                    position: fixed;
                    width: 15px;
                    height: 15px;
                    background: linear-gradient(45deg, #22c55e, #16a34a);
                    border-radius: 0 100% 0 100%;
                    z-index: -1;
                    animation: forestLeafFall 8s linear infinite;
                }
                @keyframes forestLeafFall {
                    0% {
                        transform: translateY(-100px) rotate(0deg);
                        opacity: 0;
                    }
                    10% {
                        opacity: 1;
                    }
                    50% {
                        transform: translateY(50vh) rotate(180deg);
                    }
                    90% {
                        opacity: 1;
                    }
                    100% {
                        transform: translateY(100vh) rotate(360deg);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }

        const createLeaf = () => {
            if (!this.effectsEnabled || this.currentTheme !== 'forest') return;
            
            const leaf = document.createElement('div');
            leaf.className = 'forest-leaf';
            leaf.style.left = Math.random() * window.innerWidth + 'px';
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
                this.intervals.delete('forestLeaves');
            }
        }, this.isMobile ? 3000 : 2500);
        
        this.intervals.set('forestLeaves', leafInterval);
    }

    // ============= OCEAN EFFECTS - HOÀN TOÀN MỚI =============
    initOceanEffects() {
        console.log('Initializing Ocean Effects...');
        this.createOceanFish();
        this.createOceanBubbles();
        this.initOceanMouseBubbles();
        this.initOceanHoverRipple();
        this.initOceanClickRipple();
    }

    createOceanFish() {
        console.log('Creating ocean fish...');
        
        const fishTypes = [
            { class: 'fish-large', count: this.isMobile ? 2 : 3, interval: 25000 },
            { class: 'fish-small', count: this.isMobile ? 3 : 5, interval: 18000 },
            { class: 'fish-tropical', count: this.isMobile ? 2 : 3, interval: 22000 }
        ];

        fishTypes.forEach(fishType => {
            const createFish = () => {
                if (!this.effectsEnabled || this.currentTheme !== 'ocean') return;

                for (let i = 0; i < fishType.count; i++) {
                    setTimeout(() => {
                        if (this.currentTheme !== 'ocean') return;

                        const fish = document.createElement('div');
                        fish.className = `ocean-fish`;
                        
                        const fishElement = document.createElement('div');
                        fishElement.className = fishType.class;
                        fish.appendChild(fishElement);

                        // Vị trí ngẫu nhiên theo chiều dọc
                        const topPosition = Math.random() * (window.innerHeight - 100) + 50;
                        fish.style.top = topPosition + 'px';

                        // Random delay để tạo hiệu ứng tự nhiên
                        const delay = Math.random() * 5;
                        fish.style.animationDelay = delay + 's';

                        document.body.appendChild(fish);

                        // Xóa cá sau khi animation hoàn thành
                        const animationDuration = fishType.interval;
                        setTimeout(() => {
                            if (fish.parentNode) {
                                fish.remove();
                            }
                        }, animationDuration + (delay * 1000));

                    }, i * 2000); // Delay giữa các con cá cùng loại
                }
            };

            // Tạo cá lần đầu
            if (this.effectsEnabled && this.currentTheme === 'ocean') {
                createFish();
            }

            // Lặp lại việc tạo cá
            const fishInterval = setInterval(() => {
                if (this.currentTheme === 'ocean' && this.effectsEnabled) {
                    createFish();
                } else if (this.currentTheme !== 'ocean') {
                    clearInterval(fishInterval);
                    this.intervals.delete(`oceanFish_${fishType.class}`);
                }
            }, fishType.interval);

            this.intervals.set(`oceanFish_${fishType.class}`, fishInterval);
        });
    }

    createOceanBubbles() {
        console.log('Creating ocean bubbles...');

        const createBubble = () => {
            if (!this.effectsEnabled || this.currentTheme !== 'ocean') return;

            const bubble = document.createElement('div');
            bubble.className = 'ocean-bubble';
            
            // Vị trí ngẫu nhiên ở dưới màn hình
            bubble.style.left = Math.random() * window.innerWidth + 'px';
            bubble.style.bottom = '-20px';
            
            // Kích thước ngẫu nhiên
            const size = 8 + Math.random() * 12;
            bubble.style.width = size + 'px';
            bubble.style.height = size + 'px';
            
            // Animation delay ngẫu nhiên
            bubble.style.animationDelay = Math.random() * 2 + 's';
            bubble.style.animationDuration = (6 + Math.random() * 4) + 's';

            document.body.appendChild(bubble);

            // Xóa bubble sau khi animation hoàn thành
            setTimeout(() => {
                if (bubble.parentNode) {
                    bubble.remove();
                }
            }, 10000);
        };

        // Tạo bubble định kỳ
        const bubbleInterval = setInterval(() => {
            if (this.currentTheme === 'ocean' && this.effectsEnabled) {
                // Tạo 1-3 bubbles mỗi lần
                const bubbleCount = 1 + Math.floor(Math.random() * 3);
                for (let i = 0; i < bubbleCount; i++) {
                    setTimeout(() => createBubble(), i * 500);
                }
            } else if (this.currentTheme !== 'ocean') {
                clearInterval(bubbleInterval);
                this.intervals.delete('oceanBubbles');
            }
        }, this.isMobile ? 3000 : 2000);

        this.intervals.set('oceanBubbles', bubbleInterval);
    }

    initOceanMouseBubbles() {
        const createMouseBubble = (x, y) => {
            const bubble = document.createElement('div');
            bubble.className = 'mouse-bubble';

            // Tạo kích thước ngẫu nhiên từ 8px đến 16px
            const size = 8 + Math.random() * 8;
            bubble.style.width = `${size}px`;
            bubble.style.height = `${size}px`;
            bubble.style.left = `${x}px`;
            bubble.style.top = `${y}px`;
            
            document.body.appendChild(bubble);
            setTimeout(() => {
                if (bubble.parentNode) {
                    bubble.remove();
                }
            }, 2000);
        };

        const moveHandler = (e) => {
            if (this.currentTheme !== 'ocean' || !this.effectsEnabled) return;

            // Tạo bong bóng ngẫu nhiên để tránh quá nhiều (20% chance)
            if (Math.random() < 0.2) {
                const offsetX = (Math.random() - 0.5) * 40;
                const offsetY = (Math.random() - 0.5) * 40;
                createMouseBubble(e.clientX + offsetX, e.clientY + offsetY);
            }
        };

        document.addEventListener('mousemove', moveHandler);
    }

    initOceanHoverRipple() {
        // Áp dụng class ripple-hover vào tất cả các thẻ cần hiệu ứng hover
        const elements = document.querySelectorAll('button, .card, .nav-link, .list-group-item, .btn');
        elements.forEach(el => {
            if (!el.classList.contains('ripple-hover')) {
                el.classList.add('ripple-hover');
                if (getComputedStyle(el).position === 'static') {
                    el.style.position = 'relative';
                }
                el.style.overflow = 'hidden';
            }
        });
    }

    initOceanClickRipple() {
        const clickHandler = (e) => {
            if (this.currentTheme !== 'ocean' || !this.effectsEnabled) return;

            const ripple = document.createElement('div');
            ripple.className = 'water-ripple';
            ripple.style.left = `${e.clientX}px`;
            ripple.style.top = `${e.clientY}px`;
            document.body.appendChild(ripple);
            
            setTimeout(() => {
                if (ripple.parentNode) {
                    ripple.remove();
                }
            }, 1000);
        };

        document.addEventListener('click', clickHandler);
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

        const emberInterval = setInterval(() => {
            if (this.currentTheme === 'sunset' && this.effectsEnabled) {
                createEmber();
            } else if (this.currentTheme !== 'sunset') {
                clearInterval(emberInterval);
                this.intervals.delete('sunsetEmbers');
            }
        }, this.isMobile ? 5000 : 3500);

        this.intervals.set('sunsetEmbers', emberInterval);
    }

    // ============= UTILITY METHODS =============
    clearAllEffects() {
        console.log('Clearing all effects...');
        
        // Xóa tất cả intervals
        this.intervals.forEach((interval, key) => {
            clearInterval(interval);
        });
        this.intervals.clear();

        // Xóa tất cả animation frames
        this.animationFrames.forEach((frame, key) => {
            cancelAnimationFrame(frame);
        });
        this.animationFrames.clear();

        // Xóa tất cả hiệu ứng elements
        const effectSelectors = [
            '#galaxyCursor',
            '.shooting-star',
            '.sakura-petal',
            '.forest-leaf',
            '.ocean-fish',
            '.ocean-bubble',
            '.mouse-bubble',
            '.water-ripple',
            '.sunset-glow'
        ];

        effectSelectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(el => {
                if (el.parentNode) {
                    el.remove();
                }
            });
        });

        // Xóa ripple-hover class
        const rippleElements = document.querySelectorAll('.ripple-hover');
        rippleElements.forEach(el => {
            el.classList.remove('ripple-hover');
        });
    }

    toggleEffects() {
        const body = document.body;
        if (this.effectsEnabled) {
            body.classList.remove('effects-paused');
            // Khởi động lại effects cho theme hiện tại
            if (this.currentTheme !== 'default' && this.currentTheme !== 'dark') {
                this.applyTheme(this.currentTheme);
            }
        } else {
            body.classList.add('effects-paused');
            this.clearAllEffects();
            
            // Tạm dừng tất cả animation
            const pauseStyle = document.getElementById('pause-effects');
            if (!pauseStyle) {
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
    }

    updateEffectsForDevice() {
        // Tối ưu hiệu ứng cho mobile
        if (this.isMobile) {
            console.log('Optimizing effects for mobile device');
            // Chỉ khởi động lại effects nếu đang ở theme có effects
            if (this.currentTheme === 'ocean' && this.effectsEnabled) {
                this.clearAllEffects();
                setTimeout(() => {
                    this.initOceanEffects();
                }, 100);
            }
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
        this.clearAllEffects();
        setTimeout(() => {
            this.effectsEnabled = true;
            if (this.currentTheme !== 'default' && this.currentTheme !== 'dark') {
                this.applyTheme(this.currentTheme);
            }
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

    const currentTheme = document.body.getAttribute('data-theme');
    if (currentTheme) {
        window.themeEffects.applyTheme(currentTheme);
    }

    // Expose changeTheme globally
    window.changeTheme = (theme) => {
        window.themeEffects.applyTheme(theme);
    };

    // Performance monitor
    setInterval(() => {
        window.themeEffects.monitorPerformance();
    }, 30000);
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