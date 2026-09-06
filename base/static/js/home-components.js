// Extracted without behavior changes so homepage scripts can be browser-cached.

// Source: base/templates/modal.html
document.addEventListener('DOMContentLoaded', function() {
    const couponModal = document.getElementById('couponModal');
    const viewCouponsModal = document.getElementById('viewCouponsModal');
    const openCouponBtn = document.getElementById('openCouponModalBtn');
    const viewCouponsBtn = document.getElementById('viewCouponsBtn');
    const couponForm = document.getElementById('couponForm');
    const couponMessage = document.getElementById('couponMessage');
    
    // Simple immediate close function
    function closeModal(modal) {
        modal.classList.remove('is-open');
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
    }
    
    // Simple immediate open function
    function openModal(modal) {
        modal.classList.add('is-open');
        modal.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
    }
    
    // Open apply coupon modal
    if (openCouponBtn) {
        openCouponBtn.addEventListener('click', function(e) {
            e.preventDefault();
            openModal(couponModal);
        });
    }
    
    // Open view coupons modal
    if (viewCouponsBtn) {
        viewCouponsBtn.addEventListener('click', function(e) {
            e.preventDefault();
            loadUserCoupons();
            openModal(viewCouponsModal);
        });
    }
    
    // Close buttons - Simple and direct
    document.querySelectorAll('[data-close]').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const closeType = this.getAttribute('data-close');
            
            if (closeType === 'view-coupons') {
                closeModal(viewCouponsModal);
            } else if (closeType === 'apply') {
                closeModal(couponModal);
            }
        });
    });
    
    // Prevent clicks inside modal dialog from closing
    document.querySelectorAll('.coupon-modal__dialog').forEach(function(dialog) {
        dialog.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    });
    
    // Close on ESC key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            if (couponModal.classList.contains('is-open')) {
                closeModal(couponModal);
            }
            if (viewCouponsModal.classList.contains('is-open')) {
                closeModal(viewCouponsModal);
            }
        }
    });
    
    // Apply coupon form submission
    if (couponForm) {
        couponForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const couponCode = document.getElementById('couponCode').value.trim();
            
            if (!couponCode) {
                showCouponMessage('Please enter a coupon code', 'error');
                return;
            }
            
            const submitBtn = couponForm.querySelector('.coupon-form__apply');
            const originalText = submitBtn.textContent;
            submitBtn.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Applying...';
            submitBtn.disabled = true;
            
            fetch('/apply-coupon/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    coupon_code: couponCode
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showCouponMessage(data.message, 'success');
                    document.getElementById('couponCode').value = '';
                    setTimeout(() => {
                        closeModal(couponModal);
                    }, 2000);
                } else {
                    showCouponMessage(data.message, 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showCouponMessage('An error occurred. Please try again.', 'error');
            })
            .finally(() => {
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            });
        });
    }
    
    function showCouponMessage(message, type) {
        if (couponMessage) {
            couponMessage.textContent = message;
            couponMessage.className = `coupon-form__message ${type}`;
            couponMessage.style.display = 'block';
            
            setTimeout(() => {
                couponMessage.style.display = 'none';
            }, 5000);
        }
    }
    
    function loadUserCoupons() {
        const couponsList = document.getElementById('couponsList');
        couponsList.innerHTML = '<div style="text-align: center; padding: 40px; color: #999;"><i class="fa fa-spinner fa-spin" style="font-size: 32px;"></i><br><br>Loading your coupons...</div>';
        
        fetch('/my-coupons/')
        .then(response => response.json())
        .then(data => {
            if (data.coupons && data.coupons.length > 0) {
                couponsList.innerHTML = data.coupons.map(coupon => `
                    <div class="coupon-item ${coupon.is_expired ? 'expired' : ''}">
                        <div class="coupon-status status-${coupon.is_expired ? 'expired' : 'active'}">
                            ${coupon.is_expired ? 'Expired' : 'Active'}
                        </div>
                        <div class="coupon-header">
                            <span class="coupon-code">${coupon.code}</span>
                            <span class="coupon-discount">${coupon.discount_display}</span>
                        </div>
                        ${coupon.description ? `<div class="coupon-description">${coupon.description}</div>` : ''}
                        <div class="coupon-details">
                            <strong>Valid till:</strong> ${coupon.valid_to}<br>
                            ${coupon.minimum_amount > 0 ? `<strong>Min. order:</strong> ₹${coupon.minimum_amount}<br>` : ''}
                            <strong>Uses left:</strong> ${coupon.usage_limit - coupon.used_count}
                        </div>
                    </div>
                `).join('');
            } else {
                couponsList.innerHTML = `
                    <div class="no-coupons">
                        <i class="fa fa-ticket"></i>
                        <h4>No Coupons Available</h4>
                        <p>You don't have any coupons yet. Apply for coupons to save on your purchases!</p>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            couponsList.innerHTML = '<div style="text-align: center; padding: 40px; color: #dc3545;"><i class="fa fa-exclamation-triangle" style="font-size: 32px; margin-bottom: 15px;"></i><br><strong>Error loading coupons</strong><br>Please try again later</div>';
        });
    }
});

// Source: adminpanel/templates/components/banner_slider.html
document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('banner-slider');
    if (!container) return;
    
    let slideIndex = 0;
    const slides = container.querySelectorAll('.banner-slide');
    const totalSlides = slides.length;
    
    if (totalSlides <= 1) return;
    
    // Create fresh dots
    const dotsContainer = container.querySelector('.banner-dots');
    if (dotsContainer) {
        dotsContainer.innerHTML = '';
        
        for (let i = 0; i < totalSlides; i++) {
            const dot = document.createElement('span');
            dot.className = 'banner-dot';
            if (i === 0) dot.classList.add('active');
            dot.addEventListener('click', function() {
                currentSlide(i);
            });
            dotsContainer.appendChild(dot);
        }
    }
    
    const dots = container.querySelectorAll('.banner-dot');
    
    function showSlide(n) {
        slides.forEach(slide => slide.classList.remove('active'));
        dots.forEach(dot => dot.classList.remove('active'));
        
        slideIndex = (n + totalSlides) % totalSlides;
        
        slides[slideIndex].classList.add('active');
        dots[slideIndex].classList.add('active');
    }
    
    function nextSlide() {
        showSlide(slideIndex + 1);
    }
    
    function prevSlide() {
        showSlide(slideIndex - 1);
    }
    
    function currentSlide(n) {
        showSlide(n);
    }
    
    // Navigation buttons
    const nextBtn = container.querySelector('.banner-next');
    const prevBtn = container.querySelector('.banner-prev');
    
    if (nextBtn) nextBtn.addEventListener('click', nextSlide);
    if (prevBtn) prevBtn.addEventListener('click', prevSlide);
    
    // Auto-slide every 5 seconds
    let autoSlideInterval = setInterval(nextSlide, 5000);
    
    // Pause on hover
    container.addEventListener('mouseenter', function() {
        clearInterval(autoSlideInterval);
    });
    
    container.addEventListener('mouseleave', function() {
        autoSlideInterval = setInterval(nextSlide, 5000);
    });
});

// Source: base/templates/video_course.html
(function() {
  'use strict';
  
  // Fallback SVG placeholder
  const fallbackImage = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='225'%3E%3Crect fill='%23f0f0f0' width='400' height='225'/%3E%3Ctext fill='%23999' font-family='Arial' font-size='18' text-anchor='middle' x='200' y='120'%3ENo Image Available%3C/text%3E%3C/svg%3E";
  
  // Handle all course images on page load
  document.addEventListener('DOMContentLoaded', function() {
    const courseImages = document.querySelectorAll('.course-img-elem');
    
    courseImages.forEach(function(img) {
      // Check if image failed to load
      img.addEventListener('error', function() {
        if (this.src !== fallbackImage) {
          this.src = fallbackImage;
          console.log('Image failed to load, using fallback');
        }
      });
      
      // Check if image is already broken (for cached images)
      if (img.complete && img.naturalHeight === 0) {
        img.src = fallbackImage;
      }
    });
  });
})();

// Source: base/templates/live_class.html
function smoothScroll(carouselId, direction) {
  const carousel = document.getElementById(carouselId);
  if (!carousel) return;
  const cardWidth = carousel.querySelector('.course-card')?.offsetWidth;
  if (!cardWidth) return;
  const scrollAmount = (cardWidth + 18) * 2;
  carousel.scrollBy({ left: direction === 'left' ? -scrollAmount : scrollAmount, behavior: 'smooth' });
}

document.addEventListener('DOMContentLoaded', function () {
  const carousel = document.getElementById('live-carousel');
  if (!carousel) return;
  const leftArrow = carousel.parentElement.querySelector('.slide-arrow2.left');
  const rightArrow = carousel.parentElement.querySelector('.slide-arrow2.right');
  function updateArrows() {
    if (!leftArrow || !rightArrow) return;
    const isAtStart = carousel.scrollLeft <= 10;
    const isAtEnd = carousel.scrollLeft >= carousel.scrollWidth - carousel.clientWidth - 10;
    leftArrow.style.opacity = isAtStart ? '0.3' : '0.87';
    leftArrow.style.cursor = isAtStart ? 'default' : 'pointer';
    rightArrow.style.opacity = isAtEnd ? '0.3' : '0.87';
    rightArrow.style.cursor = isAtEnd ? 'default' : 'pointer';
  }
  carousel.addEventListener('scroll', updateArrows);
  window.addEventListener('resize', updateArrows);
  updateArrows();
});

// Source: base/templates/test_series.html
// Smooth scrolling functionality (same as video courses)
function smoothScroll(carouselId, direction) {
  const carousel = document.getElementById(carouselId);
  if (!carousel) return;
  
  const cardWidth = carousel.querySelector('.course-card')?.offsetWidth;
  if (!cardWidth) return;
  
  const gap = 18;
  const scrollAmount = (cardWidth + gap) * 2;
  const scrollLeft = direction === 'left' ? -scrollAmount : scrollAmount;
  
  carousel.scrollBy({
    left: scrollLeft,
    behavior: 'smooth'
  });
}

// Auto-hide arrows based on scroll position
document.addEventListener('DOMContentLoaded', function() {
  const carousel = document.getElementById('testseries-carousel');
  if (!carousel) return;
  
  const leftArrow = carousel.parentElement.querySelector('.slide-arrow2.left');
  const rightArrow = carousel.parentElement.querySelector('.slide-arrow2.right');
  
  function updateArrows() {
    if (!leftArrow || !rightArrow) return;
    
    const isAtStart = carousel.scrollLeft <= 10;
    const isAtEnd = carousel.scrollLeft >= carousel.scrollWidth - carousel.clientWidth - 10;
    
    leftArrow.style.opacity = isAtStart ? '0.3' : '0.87';
    leftArrow.style.cursor = isAtStart ? 'default' : 'pointer';
    
    rightArrow.style.opacity = isAtEnd ? '0.3' : '0.87';
    rightArrow.style.cursor = isAtEnd ? 'default' : 'pointer';
  }
  
  carousel.addEventListener('scroll', updateArrows);
  window.addEventListener('resize', updateArrows);
  updateArrows();
});

// Source: base/templates/e_library.html
(function() {
  'use strict';
  
  // Fallback SVG placeholder for e-books
  const fallbackImage = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='225'%3E%3Crect fill='%23f0f0f0' width='400' height='225'/%3E%3Ctext fill='%23999' font-family='Arial' font-size='18' text-anchor='middle' x='200' y='120'%3ENo Cover Available%3C/text%3E%3C/svg%3E";
  
  // Handle all e-library images on page load
  document.addEventListener('DOMContentLoaded', function() {
    const elibraryImages = document.querySelectorAll('.elibrary-img-elem');
    
    elibraryImages.forEach(function(img) {
      // Check if image failed to load
      img.addEventListener('error', function() {
        if (this.src !== fallbackImage) {
          this.src = fallbackImage;
          console.log('E-library cover image failed to load, using fallback');
        }
      });
      
      // Check if image is already broken (for cached images)
      if (img.complete && img.naturalHeight === 0) {
        img.src = fallbackImage;
      }
    });
  });
})();

// Source: base/templates/product_bundle.html
(function() {
  'use strict';
  
  // Fallback SVG placeholder for bundles
  const fallbackImage = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='225'%3E%3Crect fill='%23f0f0f0' width='400' height='225'/%3E%3Ctext fill='%23999' font-family='Arial' font-size='18' text-anchor='middle' x='200' y='120'%3ENo Bundle Image%3C/text%3E%3C/svg%3E";
  
  // Handle all bundle images on page load
  document.addEventListener('DOMContentLoaded', function() {
    const bundleImages = document.querySelectorAll('.bundle-img-elem');
    
    bundleImages.forEach(function(img) {
      // Check if image failed to load
      img.addEventListener('error', function() {
        if (this.src !== fallbackImage) {
          this.src = fallbackImage;
          console.log('Bundle image failed to load, using fallback');
        }
      });
      
      // Check if image is already broken (for cached images)
      if (img.complete && img.naturalHeight === 0) {
        img.src = fallbackImage;
      }
    });
  });
})();
