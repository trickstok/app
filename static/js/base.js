let likesAmount = "";
var video = document.querySelector(".video");
video.onchange = function () {
    video = document.querySelector('.video')
}
const duration = document.querySelector(".progress-duration");
const range = document.querySelector(".progress-range");
const bar = document.querySelector(".progress-bar");
const commentsCount = document.querySelector(".comments-head-label");
const commentsCount2 = document.querySelector(".comments");

const commentsList = document.querySelector(".comments-list");

// overlay

const overlay = document.querySelector(".overlay");
const closeOvelay = document.querySelector(".howto-close");

//
const commentsIcon = document.getElementById("comments-icon");
const commentsContainer = document.querySelector(".comments-container");
const closeComments = document.querySelector(".comments-head-close");

//

const likes = document.querySelector(".likes");
const likesIcon = document.getElementById("likes-icon");

// iife

(() => {
    video.pause();
})();

function displayTime(time) {
    const mins = Math.floor(time / 60); // devide (time | given) by 60 (mins)
    let seconds = Math.floor(time % 60); // remainder of (time | given) divided by 60
    seconds = seconds <= 9 ? `0${seconds}` : seconds;
    return `${mins}:${seconds}`;
}

function updateProgress() {
    bar.style.width = `${(video.currentTime / video.duration) * 100}%`;
    duration.textContent = `${displayTime(video.currentTime)} : ${displayTime(
        video.duration
    )}`;
}

function setProgress(e) {
    const time = e.offsetX / range.offsetWidth; // get percentage where clicked and devide by duration
    bar.style.width = `${time * 100}%`;
    video.currentTime = time * video.duration;
}

// Comments | Active |

function activateComments() {
    commentsContainer.classList.add("comments-active");
    video.pause();
    if (video.pause) {
        video.style.cursor = "pointer";
    }
}
function deactivateComments() {
    if (video.pause) {
        commentsContainer.classList.remove("comments-active");
        video.play();
        video.style.cursor = "default";
    }
}

function loadComments(id=video.id) {
    fetch(`/get-comments/${id}`
    )
        .then((response) => {
            return response.json();
        })
        .then((comments) => {
            commentsList.innerHTML = "";
            commentsCount.textContent = `${comments.length} commentaires`;
            commentsCount2.textContent = `${comments.length}`;
            comments.forEach((comment) => {
                const html = `<div class="comments-item">
          <span class="comment-top">
            <span class="comment-top-logo" style="background-image:url(${comment.profilePhoto})"></span>
            <span class="comment-top-details">
              <span class="user-name">${comment.userName}</span>
              <span class="user-time">${comment.timePosted}</span>
              <span class="user-comment">${comment.comment}</span>
            </span>
          </span>
        </div>`;
                commentsList.insertAdjacentHTML("afterbegin", html);
            });
            likesAmount = Number(likes.dataset.likes);
        });
}

function updateLikes() {
    if (likesAmount >= 1000) return;
    likesIcon.src = `https://assets.codepen.io/2629920/heart+%281%29.png`;
    likesAmount = likesAmount + 1;
    likes.textContent = `${likesAmount === 1000 ? "1K" : likesAmount}`;
}

// Event listeners

range.addEventListener("click", setProgress);
video.addEventListener("timeupdate", updateProgress);
video.addEventListener("canplay", updateProgress);
commentsIcon.addEventListener("click", activateComments);
video.addEventListener("click", deactivateComments);
closeComments.addEventListener("click", deactivateComments);
likesIcon.addEventListener("click", updateLikes);
closeOvelay.addEventListener("click", () => {
    video.play();
    overlay.style.display = "none";
});

// on load

loadComments();