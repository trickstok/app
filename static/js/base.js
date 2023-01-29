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

function openModal(id) {
    document.getElementById(id).classList.add('is-active')
}

function closeModal(id) {
    document.getElementById(id).classList.remove('is-active')
}

function showUsersResults(el, results, input) {
    htmls = []
    for (const res of results) {
        if (res.certified) {
            certified_html = `<i class="fas fa-badge-check"></i>`
        } else {
            certified_html = ''
        }
        html_user = `<article class="media has-bd-b" onclick="document.getElementById('${input.id}').value = '${res.username}'; document.getElementById('${input.id}').focused = false;" style="display: flex; justify-content: center; align-items: center; scale: 0.8; cursor: pointer;">
                  <figure class="media-left">
                    <p class="image is-rounded" style="padding-left: .5em;">
                      <img src="/media/pdp/${res.photo}" class="photo large is-rounded" alt="${res.resname}">
                    </p>
                  </figure>
                  <div class="media-content">
                    <div class="content">
                      <p>
                        <strong>${res.fullname}&nbsp;${certified_html}</strong> <br><small>@${res.username}</small>
                      </p>
                    </div>
                  </div>
               </article>`
        htmls.push(html_user)
    }
    htmls.reverse()
    el.innerHTML = htmls.join('<br>')
}

async function searchUsers(query) {
    return await fetch(`/search?q=${query}&users=true`)
        .then(resp => resp.json())
        .then(data => {
            return data.data
        })
}

function sendMessage(to, content, callback) {
    fetch('/send-message', {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: `to=${to}&content=${content}`
    })
        .then(resp => resp.json())
        .then(json => {console.log(json.message)})
    callback()
    return false
}

function refreshMessages() {
    loadMessages()
}

function loadMessages() {
    fetch('/get-new-messages')
        .then(resp => resp.json())
        .then(json => {
            data = json.data
            existing_chats = []
            for (let el of document.querySelectorAll('#other-conversations .modal')) {
                existing_chats.push(el.id)
            }
            conversations_html = ""
            for (let chat of Object.keys(data.messages)) {
                chat_user = chat
                chat = data.messages[chat_user]
                chat_id = chat[0]._id
                if (chat[0].from.username === chat_user) {
                    chat_name = chat[0].from.fullname
                    chat_image = `/media/pdp/${chat[0].from.photo}`
                } else {
                    chat_name = chat[0].to.fullname
                    chat_image = `/media/pdp/${chat[0].to.photo}`
                }
                chat_desc = chat[chat.length - 1].content.slice(0, 20) + '...'
                if (!existing_chats.includes(chat_id)) {
                    chat_html = `<div class="conversation" onclick="openModal('${chat_id}')">
                                <div class="image">
                                  <img class="photo large" style="padding-right: 0; width: 3.5em !important; height: 3.5em !important;" src="${chat_image}" alt="Notification Icon">
                                </div>
                                <div class="infos">
                                  <p class="name">${chat_name}</p>
                                  <p class="last_message" id="desc${chat_id}">${chat_desc}</p>
                                </div>
                              </div>
                              <div class="modal" id="${chat_id}">
                                  <div class="modal-background"></div>
                                  <div class="modal-content is-messages" id="chat${chat_id}">
                                      <section class="section has-padding" style="overflow: hidden; height: 77vh; padding-top: 1.5rem; padding-bottom: 1.5rem;">
                                          <div class="messages">`
                    chat.forEach(message => {
                        if (message.from.username === chat_user) {
                            html_message = document.createElement('div')
                            html_message.classList.add('message')
                            html_message.innerText = message.content
                        } else {
                            html_message = document.createElement('div')
                            html_message.classList.add('message')
                            html_message.classList.add('right')
                            html_message.innerText = message.content
                        }
                        chat_html += html_message.outerHTML
                    })
                    chat_html += `</div>
                              <div class="field has-addons" style="position: absolute; bottom: 1em;">
                                <div class="control is-expanded">
                                  <input class="input" type="text" placeholder="Message..." name="message" required>
                                </div>
                                <div class="control">
                                  <button class="button" onclick="sendMessage('${chat_user}', this.parentElement.parentElement.querySelector('input[name=message]').value, () =>{ closeModal('${chat_id}'); loadMessages() })">
                                    <i class="fas fa-paper-plane"></i>
                                  </button>
                                </div>
                              </div>
                          </section>
                          </div>
                      <button class="modal-close is-large" aria-label="close" onclick="closeModal('${chat_id}')"></button>
                      </div>`
                    conversations_html += chat_html
                } else {
                    chat_html = ''
                    chat.forEach(message => {
                        if (message.from.username === chat_user) {
                            html_message = document.createElement('div')
                            html_message.classList.add('message')
                            html_message.innerText = message.content
                        } else {
                            html_message = document.createElement('div')
                            html_message.classList.add('message')
                            html_message.classList.add('right')
                            html_message.innerText = message.content
                        }
                        chat_html += html_message.outerHTML
                    })
                    div = document.getElementById(chat_id).querySelector('.messages')
                    div.innerHTML = chat_html
                    div.children[div.children.length - 1].scrollIntoView({block: "end"})
                    document.getElementById(`desc${chat_id}`).innerText = chat[chat.length - 1].content.slice(0, 20) + '...'
                }
            }
            document.querySelector('#other-conversations').innerHTML += conversations_html
        })
}

window.setInterval(refreshMessages, 1000 * 30)

// Event listeners

document.getElementById('user-search').addEventListener('keyup', async () => {
    showUsersResults(document.querySelector('.user-dropdown'), await searchUsers(document.getElementById('user-search').value), document.getElementById('user-search'))
})
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
