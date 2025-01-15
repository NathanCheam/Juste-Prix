document.addEventListener("DOMContentLoaded", function() {
    particlesJS("particles-js", {
        "particles": {
            "number": {
                "value": 30,
                "density": {
                    "enable": true,
                    "value_area": 800
                }
            },
            "color": {
                "value": "#ffffff"
            },
            "shape": {
                "type": "star",
                "stroke": {
                    "width": 0,
                    "color": "#000000"
                },
                "polygon": {
                    "nb_sides": 5
                }
            },
            "opacity": {
                "value": 0.5,
                "random": false,
                "anim": {
                    "enable": false,
                    "speed": 1,
                    "opacity_min": 0.1,
                    "sync": false
                }
            },
            "size": {
                "value": 8,
                "random": true,
                "anim": {
                    "enable": false,
                    "speed": 40,
                    "size_min": 0.1,
                    "sync": false
                }
            },
            "line_linked": {
                "enable": false
            },
            "move": {
                "enable": true,
                "speed": 6,
                "direction": "none",
                "random": false,
                "straight": false,
                "out_mode": "out",
                "bounce": false,
                "attract": {
                    "enable": false,
                    "rotateX": 600,
                    "rotateY": 1200
                }
            }
        },
        "interactivity": {
            "detect_on": "canvas",
            "events": {
                "onhover": {
                    "enable": true,
                    "mode": "repulse"
                },
                "onclick": {
                    "enable": true,
                    "mode": "push"
                },
                "resize": true
            },
            "modes": {
                "grab": {
                    "distance": 400,
                    "line_linked": {
                        "opacity": 1
                    }
                },
                "bubble": {
                    "distance": 400,
                    "size": 40,
                    "duration": 2,
                    "opacity": 8,
                    "speed": 3
                },
                "repulse": {
                    "distance": 200,
                    "duration": 0.4
                },
                "push": {
                    "particles_nb": 4
                },
                "remove": {
                    "particles_nb": 2
                }
            }
        },
        "retina_detect": true
    });

    const toggleButton = document.getElementById('mode-toggle');
    const currentMode = localStorage.getItem('mode') || 'day-mode';
    document.body.classList.add(currentMode);

    toggleButton.addEventListener('click', () => {
        document.body.classList.toggle('day-mode');
        document.body.classList.toggle('night-mode');

        const newMode = document.body.classList.contains('night-mode') ? 'night-mode' : 'day-mode';
        localStorage.setItem('mode', newMode);
    });

    const itemDetails = document.querySelector('.item-details');
    const noteStr = itemDetails.getAttribute('data-note');
    const note = parseFloat(noteStr.split(' ')[0].replace(',', '.'));
    const stars = document.querySelectorAll('#star-rating .star');
    const noteValue = document.getElementById('note-value');

    stars.forEach((star, index) => {
        if (index < Math.round(note)) {
            star.innerHTML = '&#9733;'; // Filled star
        }
    });

    noteValue.textContent = `(${note})`;
});

$(document).ready(function() {
    $('#price-form').on('submit', function(event) {
        event.preventDefault();

        $.ajax({
            type: 'POST',
            url: $(this).attr('action'),
            data: $(this).serialize(),
            success: function(response) {
                if (response.redirect) {
                    window.location.href = response.redirect;
                } else {
                    $('#message').text(response.message);
                }
            },
            error: function(xhr, status, error) {
                console.error('Erreur lors de la soumission du formulaire:', error);
            }
        });
    });
});

document.getElementById('play-button').addEventListener('click', function() {
    $('#difficultyModal').modal('show');
});

document.querySelectorAll('.difficulty-btn').forEach(button => {
    button.addEventListener('click', function() {
        const difficulty = this.getAttribute('data-difficulty');
        window.location.href = `/start?difficulty=${difficulty}`;
    });
});

document.getElementById('toggle-score-button').addEventListener('click', function() {
    const scoreTableContainer = document.getElementById('score-table-container');
    if (scoreTableContainer.style.display === 'none' || scoreTableContainer.style.display === '') {
        scoreTableContainer.style.display = 'block';
    } else {
        scoreTableContainer.style.display = 'none';
    }
});

function toggleExpand(element) {
    element.classList.toggle('expanded');
}