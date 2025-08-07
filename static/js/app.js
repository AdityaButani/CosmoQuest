// Main application JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initializeApp();
    
    // Add event listeners
    addEventListeners();
    
    // Start animations
    startAnimations();
});

function initializeApp() {
    console.log('CosmosQuest app initialized');
    
    // Add floating animation to icons
    const icons = document.querySelectorAll('.fa-space-shuttle, .fa-rocket');
    icons.forEach(icon => {
        icon.classList.add('float-animation');
    });
}

function addEventListeners() {
    // Form submission handling
    const questForm = document.querySelector('form[action="/generate-quest"]');
    if (questForm) {
        questForm.addEventListener('submit', handleQuestSubmission);
    }
    
    // Add hover effects to feature cards
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
    
    // Topic input enhancements
    const topicInput = document.getElementById('topic');
    if (topicInput) {
        // Add example topics rotation
        const examples = [
            "Photosynthesis",
            "World War II",
            "Machine Learning",
            "Ancient Egypt",
            "Quantum Physics",
            "Climate Change",
            "DNA Replication",
            "The Renaissance",
            "Black Holes",
            "Blockchain Technology"
        ];
        
        let currentExample = 0;
        
        topicInput.addEventListener('focus', function() {
            if (!this.value) {
                this.placeholder = examples[currentExample];
                currentExample = (currentExample + 1) % examples.length;
            }
        });
        
        // Add typing animation effect
        topicInput.addEventListener('input', function() {
            this.style.borderColor = this.value.length > 0 ? '#8b5cf6' : '#6b7280';
        });
    }
}

function handleQuestSubmission(event) {
    const submitButton = event.target.querySelector('button[type="submit"]');
    const topicInput = event.target.querySelector('#topic');
    
    if (!topicInput.value.trim()) {
        event.preventDefault();
        showAlert('Please enter a topic to explore!', 'error');
        return;
    }
    
    // Show loading state
    if (submitButton) {
        const originalHTML = submitButton.innerHTML;
        submitButton.innerHTML = '<span class="loading-spinner mr-2"></span>Launching Quest...';
        submitButton.disabled = true;
        
        // Re-enable button after 10 seconds as fallback
        setTimeout(() => {
            submitButton.innerHTML = originalHTML;
            submitButton.disabled = false;
        }, 10000);
    }
}

function startAnimations() {
    // Add staggered animation to feature cards
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.6s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
    
    // Add typing effect to the main heading
    const mainHeading = document.querySelector('h2');
    if (mainHeading && mainHeading.textContent.includes('Begin Your Learning Quest')) {
        animateTyping(mainHeading);
    }
}

function animateTyping(element) {
    const text = element.textContent;
    element.textContent = '';
    element.style.borderRight = '2px solid #8b5cf6';
    
    let i = 0;
    const typeTimer = setInterval(() => {
        if (i < text.length) {
            element.textContent += text.charAt(i);
            i++;
        } else {
            clearInterval(typeTimer);
            // Remove cursor after animation
            setTimeout(() => {
                element.style.borderRight = 'none';
            }, 1000);
        }
    }, 50);
}

function showAlert(message, type = 'info') {
    // Create alert element
    const alert = document.createElement('div');
    alert.className = `fixed top-4 right-4 z-50 p-4 rounded-xl shadow-lg transition-all duration-300 transform translate-x-full`;
    
    if (type === 'error') {
        alert.classList.add('alert-error');
    } else if (type === 'success') {
        alert.classList.add('alert-success');
    } else {
        alert.className += ' bg-blue-500/20 border border-blue-500/50 text-blue-300';
    }
    
    alert.innerHTML = `
        <div class="flex items-center space-x-3">
            <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : type === 'success' ? 'check-circle' : 'info-circle'}"></i>
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-2 text-gray-400 hover:text-white">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    document.body.appendChild(alert);
    
    // Animate in
    setTimeout(() => {
        alert.classList.remove('translate-x-full');
    }, 100);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        alert.classList.add('translate-x-full');
        setTimeout(() => {
            if (alert.parentElement) {
                alert.remove();
            }
        }, 300);
    }, 5000);
}

// Utility function to add glow effect to buttons
function addGlowEffect(button) {
    button.addEventListener('mouseenter', function() {
        this.style.boxShadow = '0 0 30px rgba(139, 92, 246, 0.6)';
    });
    
    button.addEventListener('mouseleave', function() {
        this.style.boxShadow = '0 0 20px rgba(139, 92, 246, 0.3)';
    });
}

// Add glow effects to all buttons
document.querySelectorAll('button, .btn-glow').forEach(addGlowEffect);

// Add particle effect on click
document.addEventListener('click', function(e) {
    if (e.target.tagName === 'BUTTON' || e.target.closest('button')) {
        createParticleEffect(e.clientX, e.clientY);
    }
});

function createParticleEffect(x, y) {
    const colors = ['#8b5cf6', '#ec4899', '#06b6d4', '#10b981'];
    
    for (let i = 0; i < 6; i++) {
        const particle = document.createElement('div');
        particle.style.position = 'fixed';
        particle.style.left = x + 'px';
        particle.style.top = y + 'px';
        particle.style.width = '4px';
        particle.style.height = '4px';
        particle.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        particle.style.borderRadius = '50%';
        particle.style.pointerEvents = 'none';
        particle.style.zIndex = '9999';
        
        document.body.appendChild(particle);
        
        const angle = (Math.PI * 2 * i) / 6;
        const velocity = 100;
        const vx = Math.cos(angle) * velocity;
        const vy = Math.sin(angle) * velocity;
        
        let opacity = 1;
        let posX = x;
        let posY = y;
        
        const animate = () => {
            opacity -= 0.05;
            posX += vx * 0.02;
            posY += vy * 0.02;
            
            particle.style.left = posX + 'px';
            particle.style.top = posY + 'px';
            particle.style.opacity = opacity;
            
            if (opacity > 0) {
                requestAnimationFrame(animate);
            } else {
                particle.remove();
            }
        };
        
        requestAnimationFrame(animate);
    }
}

// Smooth scrolling for internal links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Enter to submit form
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const form = document.querySelector('form[action="/generate-quest"]');
        if (form) {
            form.dispatchEvent(new Event('submit', { cancelable: true }));
        }
    }
    
    // Escape to clear topic input
    if (e.key === 'Escape') {
        const topicInput = document.getElementById('topic');
        if (topicInput && document.activeElement === topicInput) {
            topicInput.value = '';
            topicInput.blur();
        }
    }
});
