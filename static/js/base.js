let tags_string, html, username, load

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
const searchInput = document.getElementById('searchinput')
var nextVideoObject

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
    const time = e.offsetX / range.offsetWidth;
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

function search() {
    query = searchInput.value
    fetch(`/search?q=${query}`)
        .then(resp => resp.json())
        .then(data => {
            let users_results = data.data.users
            let videos_results = data.data.videos

            html = ''
            videos_results.forEach(result => {
                let result_description;
                if (result.description.length > 21) {
                    result_description = result.description.slice(0, 17) + '...'
                } else {
                    result_description = result.description
                }
                html += `
                <div class="video-card">
                  <div class="video-media" onclick="location.href = '/home?video=${result.video_id}'">
                    <video poster="/media/videos/${result.video_id}/thumbnail">
                        <source src="/media/videos/${result.video_id}/thumbnail" type="video/mp4" />
                    </video>
                  </div>
                  <div class="video-footer">
                    <p class="desc">
                      ${result_description}
                    </p>
                    <div class="actions">
                      <div class="views"><i class="fas fa-eye"></i>&nbsp;${result.views}</div>
                      <div class="likes" ><i class="fas fa-heart"></i>&nbsp;${result.likes_count}</div>
                      <div class="comments" ><i class="fas fa-comment"></i>&nbsp;${result.comment_count}</div>
                    </div>
                  </div>
                </div>
                `
            })
            document.getElementById('results-videos-tab').innerHTML = html

            html = ''
            users_results.forEach(user => {
                let certified_html;
                if (user.certified) {
                    certified_html = `<i class="fas fa-badge-check"></i>`
                } else {
                    certified_html = ''
                }
                html += `
                <article class="media has-bd-b" style="cursor: pointer" onclick="location.href = '/u/${user.username}'">
                  <figure class="media-left">
                    <p class="image is-rounded" style="padding-left: .5em;">
                      <img src="/media/pdp/${user.photo}" class="photo large is-rounded" alt="${user.username}">
                    </p>
                  </figure>
                  <div class="media-content">
                    <div class="content">
                      <p>
                        <strong>${user.fullname}&nbsp;${certified_html}</strong> <small>@${user.username}</small>
                        <br>
                        ${user.description}
                      </p>
                    </div>
                  </div>
               </article>
                `
            })

            document.getElementById('results-users-tab').innerHTML = html
        })
}

function fetchNextVideo() {
    fetch(`/watch?different_of=${videoID}`)
        .then(resp => resp.json())
        .then(data => {
            nextVideoObject = data.data
            document.createElement('img').src = `/media/videos/${nextVideoObject.video_id}/thumbnail`
        })
}

function loadNewVideo() {
    // Swipe -> loadNewVideo (affiche video) -> fetchNextVideo (charge la thumbnail de la prochaine vidéo)

    load = async () => {
        likesIcon.classList.remove('active')
        videoObject = nextVideoObject
        if (videoObject.liked) {
            likesIcon.classList.add('active')
        }
        videoID = videoObject.video_id
        video.setAttribute('data-id', videoID)
        tags_string = ''
        for (const tag of videoObject.tags) {
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
        commentsList.innerHTML = ''
        for (const comment of videoObject.comments) {
            html = `
        <div class="comments-item">
            <span class="comment-top">
              <span class="comment-top-logo image is-rounded"><img src="/media/pdp/${comment.user.photo}" class="photo is-rounded"></span>
              <span class="comment-top-details">
                <span class="user-name">${comment.user.fullname}</span>
                <span class="user-time">${comment.user.username}</span>
                <span class="user-comment">${comment.content}</span>
              </span>
            </span>
          </div>`
            commentsList.insertAdjacentHTML("afterbegin", html);
        }

        setTimeout(() => {
            video.poster = `/media/videos/${videoID}/thumbnail`
            video.src = `/media/videos/${videoID}`
        }, 1000)
    }

    load().then(() => {
            fetchNextVideo()
        })
}

function like() {
    if (videoObject.liked) {
        likesIcon.classList.remove('active')
        fetch(`/unlike/${videoID}`)
        videoObject.liked = false
    } else {
        likesIcon.classList.add('active')
        fetch(`/like/${videoID}`)
        videoObject.liked = true
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
addButton.addEventListener('click', () => {
    location.href = '/add'
})
