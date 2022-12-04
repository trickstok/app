let tag, tags_string, html, username

var video = document.querySelector(".video");
video.onchange = function () {
    video = document.querySelector('.video')
}
var history = []

const duration = document.querySelector(".progress-duration");
const range = document.querySelector(".progress-range");
const bar = document.querySelector(".progress-bar");

const description = document.querySelector('.video-infos .desc')
const user = document.querySelector('.video-infos .user')
const userPp = document.querySelector('#userpp')
const likes = document.querySelector('.icon-label.likes')
const comment = document.querySelector('.icon-label.comments')
const to_profile = document.querySelectorAll('.to-profile')

function open(el) {
    username = el.getAttribute('link')
    location.href = `/u/${username}`
}

to_profile.forEach(el => {
    el.addEventListener('click', () => {
        open(el)
    })
})

const commentsCount = document.querySelector(".comments-head-label");
const commentsCount2 = document.querySelector(".comments");

const commentsList = document.querySelector(".comments-list");
const commentsIcon = document.getElementById("comments-icon");
const commentsContainer = document.querySelector(".comments-container");
const closeComments = document.querySelector(".comments-head");

//

const likesIcon = document.querySelector('.likesicon')
const addButton = document.getElementById('add');

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
    pause(true)
    video.style.cursor = "pointer";
}
function deactivateComments() {
    pause()
    commentsContainer.classList.remove("comments-active");
    video.style.cursor = "default";

}

// function loadComments(id=video.id) {
//     fetch(`/get-comments/${id}`
//     )
//         .then((response) => {
//             return response.json();
//         })
//         .then((comments) => {
//             commentsList.innerHTML = "";
//             commentsCount.textContent = `${comments.length} commentaires`;
//             commentsCount2.textContent = `${comments.length}`;
//             comments.forEach((comment) => {
//                 const html = `<div class="comments-item">
//           <span class="comment-top">
//             <span class="comment-top-logo" style="background-image:url(${comment.profilePhoto})"></span>
//             <span class="comment-top-details">
//               <span class="user-name">${comment.userName}</span>
//               <span class="user-time">${comment.timePosted}</span>
//               <span class="user-comment">${comment.comment}</span>
//             </span>
//           </span>
//         </div>`;
//                 commentsList.insertAdjacentHTML("afterbegin", html);
//             });
//         });
//     likesAmount = 999;
//     likesIcon.setAttribute('style', '')
//     likes.textContent = `${likesAmount === 1000 ? "1K": likesAmount}`;
//     nametest = document.querySelector('.user-name').innerHTML;
//     if (nametest.length >= maxNameLen) {
//         nametest = nametest.split('').slice(0, maxNameLen - 3).join('') + '...'
//     }
//     userName.innerHTML = '@' + nametest
//     userPP.src = '/randompp'
// }

function pause(forcePause=false) {
    if (forcePause) {
        video.pause();
        changePause('fa-pause fa-2x', true)
    } else if (video.paused) {
        changePause('fa-play fa-2x', false)
        video.play();
    } else {
        video.pause();
        changePause('fa-pause fa-2x', true)
    }
}

function loadNewVideo() {

    fetch(`/watch`)
        .then(resp => resp.json())
        .then(data => {
            console.log(data)
            likesIcon.classList.remove('active')
            videoObject = data.data
            if (videoObject.liked) {
                likesIconAnim
                likesIcon.classList.add('active')
            }
            history.push(videoObject)
            videoID = videoObject.video_id
            video.setAttribute('data-id', videoID)
            tags_string = ''
            for (tag of videoObject.tags) {
                tags_string += `#${tag} `
            }
            description.innerText = `${videoObject.description} ${tags_string}`
            user.innerText = `${videoObject.user.username}`
            if (videoObject.user.certified) {
                user.innerHTML += '&nbsp;<i class="fas fa-badge-check"></i>'
            }
            userPp.src = `/media/pdp/${videoObject.user.photo}`
            to_profile.forEach(el => {
                el.setAttribute('link', videoObject.user.username)
            })
            likes.innerText = videoObject.likes_count
            commentsCount.innerText = `${videoObject.comment_count} commentaires`
            commentsCount2.innerText = videoObject.comment_count
            for (comment of videoObject.comments) {
                html = `<div class="comments-item">
                          <span class="comment-top">
                            <span class="comment-top-logo" style="background-image:url(/media/pdp/${comment.user.photo})"></span>
                            <span class="comment-top-details">
                              <span class="user-name">${comment.user.fullname}</span>
                              <span class="user-time">${comment.user.username}</span>
                              <span class="user-comment">${comment.content}</span>
                            </span>
                          </span>
                        </div>`
                commentsList.insertAdjacentHTML("afterbegin", html);
            }
            video.src = `/media/videos/${videoID}`
        })
}

function like() {
    if (videoObject.liked) {
        likesIcon.classList.remove('active')
        fetch(`/unlike/${videoID}`)
    } else {
        likesIcon.classList.add('active')
        fetch(`/like/${videoID}`)
    }
}

// Event listeners

range.addEventListener("click", setProgress);
video.addEventListener("timeupdate", updateProgress);
video.addEventListener("canplay", updateProgress);
video.addEventListener('dblclick', like)
video.addEventListener('click', () => {
    pause()
})
commentsIcon.addEventListener("click", activateComments);
closeComments.addEventListener("click", deactivateComments);
likesIcon.addEventListener("click", like);
addButton.addEventListener('click', () => {
    location.href = '/add'
})
