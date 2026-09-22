type UserTokenResponse = {
    id: string;
    secret: string;
};

type PublicUserInfo = {
    id: string;
    name: string;
    leader: boolean;
    lobbyId: string | null;
};

type LobbyResponse = {
    id: string;
    name: string;
    maxMembers: number;
    currMembers: number;
    needsSecret: boolean;
};

async function getNewUserId() {
    let response = await fetch(
        "/api/v1/user/new", {
            method: "POST"
        }
    );
    if (response.ok) {
        let tokenResponse: UserTokenResponse = await response.json();
        let userAuthToken = `${tokenResponse.id}\$${tokenResponse.secret}`;
        console.debug(`Got new user auth token: ${userAuthToken}`);
        localStorage.setItem("userId", tokenResponse.id);
        localStorage.setItem("userSecret", tokenResponse.secret);
        return tokenResponse.id;
    } else {
        console.log("Couldn't get session token.");
        return null;
    }
};

enum MessageType {
    Info = "info",
    Success = "success",
    Warning = "warning",
    Error = "error",
};

export async function sendUINotification(message: string, type: MessageType = MessageType.Info, temporary: boolean, pushNotification : boolean) {
    console.log(`Sending ${type} notification with message:`, message);

    //Create div, set styling
    const notificationDiv = document.createElement('div');
    notificationDiv.classList.add('alert');
    notificationDiv.classList.add(type.toString());

    //add notification message
    const notificationMessage = document.createTextNode(message);
    notificationDiv.appendChild(notificationMessage);

    //add close button to div, if it is not temporary
    if(!temporary){
        const notificationCloseButton = document.createElement('span');
        notificationCloseButton.innerHTML = '&times;';
        notificationCloseButton.classList.add('closebtn');

        notificationCloseButton.onclick = () => {
            notificationDiv.style.opacity = "0";
            setTimeout(() => {
                notificationDiv.remove();
            }, 600);
        };
        notificationDiv.appendChild(notificationCloseButton);
    }

    //show notification on screen 
    document.getElementById('notification-box')?.appendChild(notificationDiv);

    if(temporary){
        //delay before disappearing, in seconds
        let delayTime=1;

        //amount of time it fades away for, in seconds
        let fadeTime=2;

        //Set original opacity and add transition for it to fade out
        notificationDiv.style.opacity="100%";
        notificationDiv.style.transition=`all ${fadeTime}s ${delayTime}s`;
        notificationDiv.offsetHeight;

        //notification will fade until this opacity is reached
        notificationDiv.style.opacity="0%";

        //actually delete element after it fades out
        setTimeout(() => {
            notificationDiv.remove();
        }, delayTime*1000+fadeTime*1000);
    }

}

let currentLobby: LobbyResponse | null = null;

async function createLobbyCard(lobby: LobbyResponse) {
    const node = document
        .getElementById("lobby-template")!
        .firstElementChild
        ?.cloneNode(true) as HTMLElement | null;
    if (node == null) {
        return null;
    }

    node.dataset["lobbyId"] = lobby.id;

    return node;
}

async function refreshLobbies() {
    const lobbyListElement = document.getElementById("lobbies-list");
    if (lobbyListElement == null) return;

    let response = await fetch("/api/latest/lobby/all");
    if (!response.ok) {
        console.error(`Failed to get lobbies: Status code from fetching lobbies is ${response.status}`);
    }

    let lobbyList = await response.json() as LobbyResponse[];

    let newChildren: Node[] = (await Promise.all(lobbyList.map(createLobbyCard))).filter((lobby) => lobby !== null);

    if (newChildren.length == 0) {
        const template = document.getElementById("no-lobbies-template")! as HTMLTemplateElement;
        const noLobbyElement = template
            .content
            .cloneNode(true);
        newChildren.push(noLobbyElement);
    }

    lobbyListElement.replaceChildren(...newChildren);
}

async function updateLobbyUI() {
    const createButton = document.getElementById("create-lobby-button");
    const leaveButton = document.getElementById("leave-lobby-button");

    const inLobby = currentLobby !== null;

    if (createButton !== null) createButton.hidden =  inLobby;
    if (leaveButton  !== null) leaveButton.hidden  = !inLobby;
}

let activeWindow = "home";
setPageContent("home")

// attach event listeners to all the buttons on the frontend
document.addEventListener("DOMContentLoaded", () => {
    // make the sidenav buttons actually toggle the active frame

    const sidenavButtonHome = document.getElementById("sidenav-link-home");
    const sidenavButtonLobbies = document.getElementById("sidenav-link-lobbies");
    const sidenavButtonChat = document.getElementById("sidenav-link-chat");

    if (sidenavButtonHome)
        sidenavButtonHome.addEventListener('click', () => setPageContent("home"));
    if (sidenavButtonLobbies)
        sidenavButtonLobbies.addEventListener('click', () => setPageContent("lobbies","lobby-main"));
    if (sidenavButtonChat)
        sidenavButtonChat.addEventListener('click', () => setPageContent("chat"));

});

async function getUserInfo(userId: string) {
    let response = await fetch(`/api/v1/user/info?user_id=${userId}`, {
        credentials: "omit",
    });
    if (response.ok) {
        let infoResponse: PublicUserInfo = await response.json();
        return infoResponse;
    } else if (response.status == 502) {
        // this means there was a gateway error, which is probably because the backend is down
        await sendUINotification("The backend server seems to be down. Try checking back in in a couple hours, or contact the hostmaster.", MessageType.Error, false, true)
        return null;
    } else {
        console.log(`Couldn't get user info for user ${userId}, since response code was ${response.status}.`);
        return null;
    }
};

async function start () {
    console.log("start initialized");
    let userId = localStorage.getItem("userId");
    if (userId == null) {
        console.log("Don't have a userString, getting a new one!");
        userId = await getNewUserId();
        if (userId == null) {
            // wait 15 seconds until next request
            setTimeout(start, 15000);
            return
        }
    }
    // check if still active
    let selfInfo = await getUserInfo(userId);
    if (selfInfo == null) {
        // couldn't get user info, just return
        return;
    }
    // set username
    let usernameElement = document.getElementById("username")
    if (usernameElement != null)
        usernameElement.textContent = selfInfo.name
    // check to see if the user is in a lobby
    if (selfInfo.lobbyId != null) {
        // if it is in a lobby, figure out the lobby name
    }
};

window.addEventListener('load', async () => {
    await start();
})

const centerContent: HTMLDivElement =document.querySelector("#center-content")!

async function setPageContent(location: NonNullable<string>,divId?: string){
    activeWindow=location
    console.log("Changing location to: "+activeWindow)
    
    //use div with same name as location, if null
    if(!divId){
        divId=location
    }

    //Fetch html from template 
    const htmlFetchResponse= await fetch(`templates/${location}.html`)
     if (!htmlFetchResponse.ok) {
      throw new Error(`Response status: ${htmlFetchResponse.status}`);
    }
    
    //convert response to html
    const pageText=await htmlFetchResponse.text()
    const parser=new DOMParser()
    const pageHTML= parser.parseFromString(pageText, "text/html")

    if(pageHTML){
        //add template to centerContent
        const divTemplate : HTMLTemplateElement | null = pageHTML.querySelector(`#${divId}`)
        if(divTemplate){
            const lobbyBody=document.importNode(divTemplate.content, true)
            centerContent.replaceChildren(lobbyBody)
        }else{
            console.error(`'${divTemplate}'+ is not a valid not div name`)
        }
    }

    //Make any other dynamically added page-changing buttons interactive
    const locationButtons : (HTMLButtonElement | HTMLLinkElement)[] =Array.from(document.querySelectorAll(".pageChange"))
    if(locationButtons.length>0){
        for(let button of locationButtons){
            let location : string = button.getAttribute("data-url") || ""
            let div :string =button.getAttribute("data-div") || ""
            button.addEventListener("click",()=>{
                setPageContent(location,div)
            })
        }
    }

    //location-specific code to run on page change
    switch (location){
        case "lobbies":{
            void refreshLobbies();
            void updateLobbyUI();
            break;
        }
        case "home":{
            //setup ping button
            const pingButton = document.getElementById("ping-button");
            if (pingButton) {
                pingButton.onclick = () => sendUINotification("pong!",undefined,true,true);
            }
            break
        }
    }
}