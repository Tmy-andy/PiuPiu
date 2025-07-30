// ===== UNIVERSAL MODAL FIX CHO TẤT CẢ MODAL =====
document.addEventListener('DOMContentLoaded', function() {
    // Universal Modal Fix
    const initUniversalModalFix = () => {
        const modals = document.querySelectorAll('.modal');
        const mobileNavToggle = document.querySelector('.mobile-nav-toggle');
        const mobileNavDropdown = document.querySelector('.mobile-nav-dropdown');
        const mobileNavOverlay = document.querySelector('.mobile-nav-overlay');
        
        modals.forEach(modal => {
            const modalId = modal.id;
            
            // Khi modal bắt đầu mở
            modal.addEventListener('show.bs.modal', function(event) {
                console.log(`Modal ${modalId} opening...`);
                
                // Đóng mobile nav nếu đang mở
                if (mobileNavDropdown?.classList.contains('show')) {
                    mobileNavToggle?.classList.remove('active');
                    mobileNavDropdown?.classList.remove('show');
                    mobileNavOverlay?.classList.remove('show');
                }
                
                // Thêm class để CSS có thể target
                document.body.classList.add('modal-opening', `${modalId}-active`);
                
                // Fix cho iOS Safari viewport
                if (/iPad|iPhone|iPod/.test(navigator.userAgent)) {
                    const viewport = document.querySelector('meta[name=viewport]');
                    if (viewport) {
                        const originalContent = viewport.getAttribute('content');
                        viewport.setAttribute('data-original-content', originalContent);
                        viewport.setAttribute('content', 
                            'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no');
                    }
                }
                
                // Đảm bảo z-index cao nhất
                setTimeout(() => {
                    modal.style.zIndex = '99999';
                    const backdrop = document.querySelector('.modal-backdrop');
                    if (backdrop) {
                        backdrop.style.zIndex = '99998';
                    }
                }, 10);
            });
            
            // Khi modal đã mở hoàn toàn
            modal.addEventListener('shown.bs.modal', function() {
                console.log(`Modal ${modalId} opened`);
                document.body.classList.remove('modal-opening');
                document.body.classList.add('modal-active');
                
                // Focus vào modal để đảm bảo accessibility và touch events
                modal.focus();
                
                // Fix custom select dropdowns (cho game history)
                const customSelects = modal.querySelectorAll('.custom-select');
                customSelects.forEach(select => {
                    const dropdown = select.querySelector('.select-dropdown');
                    if (dropdown) {
                        dropdown.style.zIndex = '100001';
                    }
                });
                
                // Fix scrolling trên mobile
                if (window.innerWidth <= 991) {
                    // Lưu vị trí scroll hiện tại
                    const scrollY = window.scrollY;
                    document.body.style.position = 'fixed';
                    document.body.style.top = `-${scrollY}px`;
                    document.body.style.width = '100%';
                    document.body.style.overflow = 'hidden';
                    document.body.setAttribute('data-scroll-y', scrollY);
                }
            });
            
            // Khi modal bắt đầu đóng
            modal.addEventListener('hide.bs.modal', function() {
                console.log(`Modal ${modalId} closing...`);
                document.body.classList.remove('modal-active', `${modalId}-active`);
                
                // Reset scrolling trên mobile
                if (window.innerWidth <= 991) {
                    const scrollY = document.body.getAttribute('data-scroll-y');
                    document.body.style.position = '';
                    document.body.style.top = '';
                    document.body.style.width = '';
                    document.body.style.overflow = '';
                    if (scrollY) {
                        window.scrollTo(0, parseInt(scrollY));
                        document.body.removeAttribute('data-scroll-y');
                    }
                }
            });
            
            // Khi modal đã đóng hoàn toàn
            modal.addEventListener('hidden.bs.modal', function() {
                console.log(`Modal ${modalId} closed`);
                
                // Reset viewport cho iOS
                if (/iPad|iPhone|iPod/.test(navigator.userAgent)) {
                    const viewport = document.querySelector('meta[name=viewport]');
                    if (viewport) {
                        const originalContent = viewport.getAttribute('data-original-content');
                        if (originalContent) {
                            viewport.setAttribute('content', originalContent);
                            viewport.removeAttribute('data-original-content');
                        } else {
                            viewport.setAttribute('content', 'width=device-width, initial-scale=1.0');
                        }
                    }
                }
                
                // Reset z-index
                modal.style.zIndex = '';
                
                // Reset custom select dropdowns
                const customSelects = modal.querySelectorAll('.custom-select');
                customSelects.forEach(select => {
                    const dropdown = select.querySelector('.select-dropdown');
                    if (dropdown) {
                        dropdown.classList.remove('show');
                        dropdown.style.zIndex = '';
                    }
                });
                
                // Reset form
                const form = modal.querySelector('form');
                if (form) {
                    form.reset();
                }
            });
            
            // Fix touch events cho modal trên mobile
            if (window.innerWidth <= 991) {
                modal.addEventListener('touchstart', function(e) {
                    e.stopPropagation();
                });
                
                modal.addEventListener('touchmove', function(e) {
                    // Cho phép scroll trong các element cần thiết
                    const modalBody = modal.querySelector('.modal-body');
                    const selectDropdowns = modal.querySelectorAll('.select-dropdown');
                    const selectedItems = modal.querySelectorAll('.selected-items');
                    
                    let allowScroll = false;
                    
                    // Check nếu touch trong modal-body
                    if (modalBody && modalBody.contains(e.target)) {
                        allowScroll = true;
                    }
                    
                    // Check nếu touch trong select-dropdown
                    selectDropdowns.forEach(dropdown => {
                        if (dropdown.contains(e.target)) {
                            allowScroll = true;
                        }
                    });
                    
                    // Check nếu touch trong selected-items
                    selectedItems.forEach(container => {
                        if (container.contains(e.target)) {
                            allowScroll = true;
                        }
                    });
                    
                    if (!allowScroll) {
                        e.preventDefault();
                    }
                });
            }
            
            // Fix custom select dropdown positioning trên mobile
            const customSelects = modal.querySelectorAll('.custom-select');
            customSelects.forEach(select => {
                const header = select.querySelector('.select-header');
                const dropdown = select.querySelector('.select-dropdown');
                
                if (header && dropdown) {
                    header.addEventListener('click', function() {
                        if (window.innerWidth <= 991) {
                            // Đảm bảo dropdown có z-index cao
                            dropdown.style.zIndex = '100001';
                            
                            // Fix positioning nếu cần
                            setTimeout(() => {
                                const rect = select.getBoundingClientRect();
                                const modalRect = modal.getBoundingClientRect();
                                
                                // Nếu dropdown bị tràn ra ngoài modal
                                if (rect.bottom + 200 > modalRect.bottom) {
                                    dropdown.style.top = 'auto';
                                    dropdown.style.bottom = '100%';
                                    dropdown.style.borderRadius = '0.375rem 0.375rem 0 0';
                                } else {
                                    dropdown.style.top = '100%';
                                    dropdown.style.bottom = 'auto';
                                    dropdown.style.borderRadius = '0 0 0.375rem 0.375rem';
                                }
                            }, 10);
                        }
                    });
                }
            });
        });
        
        // Ngăn mobile nav toggle khi modal đang mở
        if (mobileNavToggle) {
            mobileNavToggle.addEventListener('click', function(e) {
                if (document.body.classList.contains('modal-active')) {
                    e.preventDefault();
                    e.stopPropagation();
                    return false;
                }
            });
        }
        
        // Listen for dynamically added modals
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1 && node.classList && node.classList.contains('modal')) {
                        console.log('New modal detected:', node.id);
                        // Re-init for new modal
                        setTimeout(() => initUniversalModalFix(), 100);
                    }
                });
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    };
    
    // Initialize
    initUniversalModalFix();
    
    // Debug functions
    window.debugModalZIndex = function() {
        const modals = document.querySelectorAll('.modal');
        const backdrop = document.querySelector('.modal-backdrop');
        const mobileNav = document.querySelector('.mobile-nav');
        
        console.log('=== MODAL Z-INDEX DEBUG ===');
        modals.forEach((modal, index) => {
            const computedStyle = getComputedStyle(modal);
            console.log(`Modal ${index} (${modal.id}):`, {
                'z-index': computedStyle.zIndex,
                'position': computedStyle.position,
                'display': computedStyle.display
            });
        });
        
        if (backdrop) {
            console.log('Backdrop z-index:', getComputedStyle(backdrop).zIndex);
        }
        
        if (mobileNav) {
            console.log('Mobile nav z-index:', getComputedStyle(mobileNav).zIndex);
        }
        
        console.log('Body classes:', document.body.className);
    };
    
    window.forceModalToTop = function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.zIndex = '999999';
            const backdrop = document.querySelector('.modal-backdrop');
            if (backdrop) {
                backdrop.style.zIndex = '999995';
            }
            console.log(`Forced ${modalId} to top`);
        }
    };
    
    // Test function cho mobile
    window.testModalOnMobile = function() {
        const testModal = document.querySelector('.modal');
        if (testModal) {
            const modal = new bootstrap.Modal(testModal);
            modal.show();
        }
    };
});