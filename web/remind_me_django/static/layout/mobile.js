const mobile_nav_btn = document.querySelector('.mobile-sidebar-btn');
const mobile_nav = document.getElementById('mobile-sidebar');
const page_body = document.getElementsByTagName('body')[0];



mobile_nav_btn.addEventListener('click', openMenu);

function openMenu(e){
    console.log('clicked');
    const mobile_classList = Array.from(mobile_nav.classList);
    
    // If the navbar is not closed, do this
    if (!(mobile_classList.includes('mobile-sidebarClosed'))){
        console.log("closing navbar");
        mobile_nav.classList.remove('mobile-sidebarOpen');
        mobile_nav_btn.classList.remove('mobile-btn-sidebarOpen');
        mobile_nav.classList.add('mobile-sidebarClosed');
        mobile_nav_btn.classList.add('mobile-btn-sidebarClosed');
        console.log('11')
        
        mobile_nav.style.width = '0%';
        page_body.style.overflow = 'visible';
    }else{
        console.log("opening navbar");
        mobile_nav.classList.remove('mobile-sidebarClosed');
        mobile_nav_btn.classList.remove('mobile-btn-sidebarClosed');
        mobile_nav.classList.add('mobile-sidebarOpen');
        mobile_nav_btn.classList.add('mobile-btn-sidebarOpen');
        console.log('11')
        
        mobile_nav.style.width = '100%';
        page_body.style.overflow = 'hidden';

    }
    console.log(page_body);
}


