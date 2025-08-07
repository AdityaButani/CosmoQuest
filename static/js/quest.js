// Quest page specific JavaScript
document.addEventListener('DOMContentLoaded', function() {
    initializeQuestPage();
    setupQuizHandling();
    addQuestAnimations();
});

function initializeQuestPage() {
    console.log('Quest page initialized');
    
    // Add intersection observer for animations
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    });
    
    // Observe all quest cards
    document.querySelectorAll('.quest-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'all 0.6s ease';
        observer.observe(card);
    });
}

function setupQuizHandling() {
    const quizForm = document.getElementById('quiz-form');
    if (quizForm) {
        quizForm.addEventListener('submit', handleQuizSubmission);
    }
}

function toggleQuestContent() {
    const questContent = document.getElementById('quest-content');
    const keyPoints = document.querySelector('.key-points');
    const visualSuggestions = document.querySelector('.visual-suggestions');
    const toggleBtn = document.getElementById('toggle-content-btn');
    const icon = toggleBtn.querySelector('i');
    
    if (questContent.style.display === 'none') {
        // Show content
        questContent.style.display = 'block';
        if (keyPoints) keyPoints.style.display = 'block';
        if (visualSuggestions) visualSuggestions.style.display = 'block';
        
        icon.className = 'fas fa-eye-slash mr-2';
        toggleBtn.innerHTML = '<i class="fas fa-eye-slash mr-2"></i>Hide Content';
    } else {
        // Hide content
        questContent.style.display = 'none';
        if (keyPoints) keyPoints.style.display = 'none';
        // Don't hide visual suggestions - they should always be visible
        // if (visualSuggestions) visualSuggestions.style.display = 'none';
        
        icon.className = 'fas fa-eye mr-2';
        toggleBtn.innerHTML = '<i class="fas fa-eye mr-2"></i>Show Content';
    }
}

async function handleQuizSubmission(event) {
    event.preventDefault();
    
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');
    const resultsDiv = document.getElementById('quiz-results');
    
    // Show loading state
    const originalButtonText = submitButton.innerHTML;
    submitButton.innerHTML = '<span class="loading-spinner mr-2"></span>Checking answers...';
    submitButton.disabled = true;
    
    try {
        // Collect answers
        const formData = new FormData(form);
        const answers = {};
        
        // Get all form inputs
        const inputs = form.querySelectorAll('input[name^="q"], select[name^="q"]');
        inputs.forEach(input => {
            if (input.type === 'radio' && input.checked) {
                answers[input.name] = input.value;
            } else if (input.type === 'text' || input.tagName === 'SELECT') {
                answers[input.name] = input.value;
            }
        });
        
        formData.set('answers', JSON.stringify(answers));
        
        // Submit quiz
        const response = await fetch('/submit-quiz', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayQuizResults(result, resultsDiv);
            
            // If quiz passed, enable quest completion
            if (result.passed) {
                setTimeout(() => {
                    showCompletionOptions(form.querySelector('input[name="quest_num"]').value);
                }, 2000);
            }
        } else {
            throw new Error(result.error || 'Quiz submission failed');
        }
        
    } catch (error) {
        console.error('Quiz submission error:', error);
        showAlert('Failed to submit quiz. Please try again.', 'error');
    } finally {
        // Restore button
        submitButton.innerHTML = originalButtonText;
        submitButton.disabled = false;
    }
}

function displayQuizResults(result, container) {
    const passed = result.passed;
    const scoreClass = passed ? 'quiz-result-success' : 'quiz-result-fail';
    const icon = passed ? 'fa-check-circle' : 'fa-times-circle';
    const message = passed ? 'Excellent work!' : 'Keep learning!';
    
    container.innerHTML = `
        <div class="${scoreClass} rounded-xl p-6 animate-pulse">
            <div class="flex items-center space-x-3 mb-4">
                <i class="fas ${icon} text-2xl"></i>
                <h4 class="text-xl font-bold">${message}</h4>
            </div>
            <div class="mb-4">
                <div class="flex items-center justify-between mb-2">
                    <span>Your Score:</span>
                    <span class="font-bold">${result.score}/${result.total} (${result.percentage}%)</span>
                </div>
                <div class="w-full bg-gray-700 rounded-full h-3">
                    <div class="bg-gradient-to-r from-green-500 to-blue-500 h-3 rounded-full transition-all duration-1000" 
                         style="width: ${result.percentage}%"></div>
                </div>
            </div>
            ${passed ? 
                '<p class="text-green-300">🎉 You passed! Ready to continue to the next quest.</p>' : 
                '<p class="text-yellow-300">💪 Review the material and try again when ready.</p>'
            }
        </div>
    `;
    
    container.classList.remove('hidden');
    
    // Add confetti effect if passed
    if (passed) {
        createConfettiEffect();
    }
}

function showCompletionOptions(questNum) {
    const questNavigation = document.querySelector('.mt-8.flex');
    if (questNavigation) {
        const completeButton = document.createElement('button');
        completeButton.onclick = () => completeQuest(questNum);
        completeButton.className = 'bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-bold py-3 px-6 rounded-xl transition-all duration-300 transform hover:scale-105 ml-auto';
        completeButton.innerHTML = '<i class="fas fa-check mr-2"></i>Complete Quest';
        
        questNavigation.appendChild(completeButton);
    }
}

async function completeQuest(questNum) {
    try {
        const formData = new FormData();
        formData.append('quest_num', questNum);
        
        const response = await fetch('/complete-quest', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            
            // Update planet progression UI
            updatePlanetProgression(result.completed_quests);
            
            // Navigate to next quest after delay
            setTimeout(() => {
                if (parseInt(questNum) < 5) {
                    window.location.href = result.next_quest_url;
                } else {
                    // Show completion celebration
                    showQuestCompletionCelebration();
                }
            }, 2000);
        } else {
            throw new Error(result.error || 'Failed to complete quest');
        }
        
    } catch (error) {
        console.error('Quest completion error:', error);
        showAlert('Failed to complete quest. Please try again.', 'error');
    }
}

function updatePlanetProgression(completedQuests) {
    const planets = document.querySelectorAll('.planet');
    planets.forEach((planet, index) => {
        const questNum = index + 1;
        if (completedQuests.includes(questNum)) {
            planet.className = 'planet completed w-12 h-12 md:w-16 md:h-16 rounded-full bg-gradient-to-br from-green-400 to-emerald-500 flex items-center justify-center text-white font-bold border-4 border-green-300 shadow-lg shadow-green-400/50 animate-pulse';
            planet.innerHTML = '<i class="fas fa-check text-lg md:text-xl"></i>';
        }
    });
}

function showQuestCompletionCelebration() {
    // Create overlay
    const overlay = document.createElement('div');
    overlay.className = 'fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center';
    
    overlay.innerHTML = `
        <div class="quest-card bg-space-card/90 backdrop-blur-sm rounded-3xl p-8 border border-purple-500/50 shadow-2xl text-center max-w-lg mx-4">
            <div class="mb-6">
                <i class="fas fa-trophy text-6xl text-yellow-400 mb-4 animate-bounce"></i>
                <h2 class="text-3xl font-bold bg-gradient-to-r from-yellow-400 to-orange-400 bg-clip-text text-transparent mb-4">
                    Quest Master!
                </h2>
                <p class="text-gray-300 text-lg">
                    Congratulations! You've successfully completed all 5 quests and mastered the topic.
                </p>
            </div>
            
            <div class="space-y-4">
                <button onclick="window.location.href='/'" class="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold py-3 px-6 rounded-xl transition-all duration-300">
                    <i class="fas fa-rocket mr-2"></i>
                    Start New Quest
                </button>
                <button onclick="this.closest('.fixed').remove()" class="w-full bg-gradient-to-r from-gray-600 to-gray-700 hover:from-gray-700 hover:to-gray-800 text-white font-bold py-3 px-6 rounded-xl transition-all duration-300">
                    <i class="fas fa-book mr-2"></i>
                    Review Quests
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(overlay);
    
    // Add celebration effects
    createConfettiEffect();
    createFireworksEffect();
}

function addQuestAnimations() {
    // Animate key points
    const keyPoints = document.querySelectorAll('ul li');
    keyPoints.forEach((point, index) => {
        point.style.opacity = '0';
        point.style.transform = 'translateX(-20px)';
        
        setTimeout(() => {
            point.style.transition = 'all 0.5s ease';
            point.style.opacity = '1';
            point.style.transform = 'translateX(0)';
        }, index * 100);
    });
    
    // Animate fun facts
    const funFacts = document.querySelectorAll('.fun-facts .bg-space-dark\\/50');
    funFacts.forEach((fact, index) => {
        fact.style.opacity = '0';
        fact.style.transform = 'scale(0.9)';
        
        setTimeout(() => {
            fact.style.transition = 'all 0.6s ease';
            fact.style.opacity = '1';
            fact.style.transform = 'scale(1)';
        }, index * 200);
    });
}

function createConfettiEffect() {
    const colors = ['#FFD700', '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'];
    const confettiCount = 50;
    
    for (let i = 0; i < confettiCount; i++) {
        setTimeout(() => {
            const confetti = document.createElement('div');
            confetti.style.position = 'fixed';
            confetti.style.left = Math.random() * window.innerWidth + 'px';
            confetti.style.top = '-10px';
            confetti.style.width = Math.random() * 8 + 4 + 'px';
            confetti.style.height = confetti.style.width;
            confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
            confetti.style.borderRadius = Math.random() > 0.5 ? '50%' : '0';
            confetti.style.pointerEvents = 'none';
            confetti.style.zIndex = '9999';
            confetti.style.transform = `rotate(${Math.random() * 360}deg)`;
            
            document.body.appendChild(confetti);
            
            const fallSpeed = Math.random() * 3 + 2;
            const horizontalSpeed = (Math.random() - 0.5) * 2;
            let rotation = 0;
            
            const animate = () => {
                const currentTop = parseFloat(confetti.style.top);
                const currentLeft = parseFloat(confetti.style.left);
                
                confetti.style.top = currentTop + fallSpeed + 'px';
                confetti.style.left = currentLeft + horizontalSpeed + 'px';
                rotation += 5;
                confetti.style.transform = `rotate(${rotation}deg)`;
                
                if (currentTop < window.innerHeight + 20) {
                    requestAnimationFrame(animate);
                } else {
                    confetti.remove();
                }
            };
            
            requestAnimationFrame(animate);
        }, i * 50);
    }
}

function createFireworksEffect() {
    const fireworkColors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFD93D', '#6BCF7F'];
    
    for (let i = 0; i < 3; i++) {
        setTimeout(() => {
            const x = Math.random() * window.innerWidth;
            const y = Math.random() * window.innerHeight * 0.5 + 100;
            
            for (let j = 0; j < 20; j++) {
                const spark = document.createElement('div');
                spark.style.position = 'fixed';
                spark.style.left = x + 'px';
                spark.style.top = y + 'px';
                spark.style.width = '3px';
                spark.style.height = '3px';
                spark.style.backgroundColor = fireworkColors[Math.floor(Math.random() * fireworkColors.length)];
                spark.style.borderRadius = '50%';
                spark.style.pointerEvents = 'none';
                spark.style.zIndex = '9999';
                
                document.body.appendChild(spark);
                
                const angle = (Math.PI * 2 * j) / 20;
                const velocity = Math.random() * 100 + 50;
                const vx = Math.cos(angle) * velocity;
                const vy = Math.sin(angle) * velocity;
                
                let opacity = 1;
                let posX = x;
                let posY = y;
                
                const animate = () => {
                    opacity -= 0.02;
                    posX += vx * 0.02;
                    posY += vy * 0.02 + 1; // gravity
                    
                    spark.style.left = posX + 'px';
                    spark.style.top = posY + 'px';
                    spark.style.opacity = opacity;
                    
                    if (opacity > 0) {
                        requestAnimationFrame(animate);
                    } else {
                        spark.remove();
                    }
                };
                
                requestAnimationFrame(animate);
            }
        }, i * 1000);
    }
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

// Add smooth transitions for quest navigation
document.querySelectorAll('a[href^="/quest/"]').forEach(link => {
    link.addEventListener('click', function(e) {
        const questCard = document.querySelector('.quest-card');
        if (questCard) {
            questCard.style.opacity = '0.5';
            questCard.style.transform = 'scale(0.95)';
        }
    });
});

// Auto-save quiz progress (optional enhancement)
function autoSaveQuizProgress() {
    const quizForm = document.getElementById('quiz-form');
    if (quizForm) {
        const inputs = quizForm.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.addEventListener('change', function() {
                const questNum = quizForm.querySelector('input[name="quest_num"]').value;
                const savedData = JSON.parse(localStorage.getItem(`quiz_progress_${questNum}`) || '{}');
                savedData[this.name] = this.value;
                localStorage.setItem(`quiz_progress_${questNum}`, JSON.stringify(savedData));
            });
        });
        
        // Restore saved progress
        const questNum = quizForm.querySelector('input[name="quest_num"]').value;
        const savedData = JSON.parse(localStorage.getItem(`quiz_progress_${questNum}`) || '{}');
        
        Object.entries(savedData).forEach(([name, value]) => {
            const input = quizForm.querySelector(`[name="${name}"]`);
            if (input) {
                if (input.type === 'radio') {
                    const radioInput = quizForm.querySelector(`[name="${name}"][value="${value}"]`);
                    if (radioInput) radioInput.checked = true;
                } else {
                    input.value = value;
                }
            }
        });
    }
}

// Initialize auto-save
autoSaveQuizProgress();

// Global variables for popup functionality
let currentImageUrl = '';
let isDragging = false;
let isResizing = false;
let startX, startY, startWidth, startHeight;

// Image popup functions
function openImagePopup(imageUrl, title, source) {
    currentImageUrl = imageUrl;
    
    // Set popup content
    document.getElementById('imagePopupTitle').textContent = title || 'Visual Learning Aid';
    document.getElementById('imagePopupSource').textContent = source || 'Educational Resource';
    document.getElementById('imagePopupImg').src = imageUrl;
    document.getElementById('imagePopupImg').alt = title || 'Visual Learning Aid';
    
    // Show popup
    const popup = document.getElementById('imagePopup');
    popup.classList.remove('hidden');
    
    // Add smooth fade-in animation
    popup.style.opacity = '0';
    setTimeout(() => {
        popup.style.transition = 'opacity 0.3s ease';
        popup.style.opacity = '1';
    }, 10);
    
    // Prevent body scroll when popup is open
    document.body.style.overflow = 'hidden';
    
    // Add escape key listener
    document.addEventListener('keydown', handleEscapeKey);
    
    // Initialize resize functionality
    initializePopupResize();
}

function closeImagePopup() {
    const popup = document.getElementById('imagePopup');
    
    // Add fade-out animation
    popup.style.transition = 'opacity 0.3s ease';
    popup.style.opacity = '0';
    
    setTimeout(() => {
        popup.classList.add('hidden');
        popup.style.opacity = '';
        popup.style.transition = '';
        
        // Restore body scroll
        document.body.style.overflow = '';
        
        // Remove escape key listener
        document.removeEventListener('keydown', handleEscapeKey);
        
        // Reset popup content size
        const popupContent = document.getElementById('imagePopupContent');
        popupContent.style.width = '';
        popupContent.style.height = '';
    }, 300);
}

function openOriginalImage() {
    if (currentImageUrl) {
        window.open(currentImageUrl, '_blank');
    }
}

function handleEscapeKey(event) {
    if (event.key === 'Escape') {
        closeImagePopup();
    }
}

function initializePopupResize() {
    const popupContent = document.getElementById('imagePopupContent');
    const resizeHandle = document.getElementById('resizeHandle');
    
    if (!resizeHandle) return;
    
    resizeHandle.addEventListener('mousedown', (e) => {
        isResizing = true;
        startX = e.clientX;
        startY = e.clientY;
        startWidth = parseInt(window.getComputedStyle(popupContent).width, 10);
        startHeight = parseInt(window.getComputedStyle(popupContent).height, 10);
        
        document.addEventListener('mousemove', handleResize);
        document.addEventListener('mouseup', stopResize);
        
        // Prevent text selection during resize
        e.preventDefault();
    });
}

function handleResize(e) {
    if (!isResizing) return;
    
    const popupContent = document.getElementById('imagePopupContent');
    const newWidth = startWidth + (e.clientX - startX);
    const newHeight = startHeight + (e.clientY - startY);
    
    // Set minimum and maximum dimensions
    const minWidth = 400;
    const minHeight = 300;
    const maxWidth = window.innerWidth * 0.9;
    const maxHeight = window.innerHeight * 0.9;
    
    if (newWidth >= minWidth && newWidth <= maxWidth) {
        popupContent.style.width = newWidth + 'px';
    }
    
    if (newHeight >= minHeight && newHeight <= maxHeight) {
        popupContent.style.height = newHeight + 'px';
    }
}

function stopResize() {
    isResizing = false;
    document.removeEventListener('mousemove', handleResize);
    document.removeEventListener('mouseup', stopResize);
}

// Close popup when clicking outside the content
document.addEventListener('DOMContentLoaded', function() {
    const popup = document.getElementById('imagePopup');
    
    if (popup) {
        popup.addEventListener('click', function(e) {
            if (e.target === popup) {
                closeImagePopup();
            }
        });
    }
});
