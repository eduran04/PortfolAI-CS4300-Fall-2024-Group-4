// initialization

const RESPONSIVE_WIDTH = 1024

let headerWhiteBg = false
let isHeaderCollapsed = window.innerWidth < RESPONSIVE_WIDTH
const collapseBtn = document.getElementById("collapse-btn")
const collapseHeaderItems = document.getElementById("collapsed-header-items")

// Initialize menu state on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        if (window.innerWidth > RESPONSIVE_WIDTH) {
            // Desktop: ensure menu is visible
            collapseHeaderItems.style.width = ""
            collapseHeaderItems.style.opacity = ""
            collapseHeaderItems.classList.remove("opacity-0", "opacity-100")
        }
    })
} else {
    // DOM already loaded
    if (window.innerWidth > RESPONSIVE_WIDTH) {
        collapseHeaderItems.style.width = ""
        collapseHeaderItems.style.opacity = ""
        collapseHeaderItems.classList.remove("opacity-0", "opacity-100")
    }
}



function onHeaderClickOutside(e) {

    if (!collapseHeaderItems.contains(e.target)) {
        toggleHeader()
    }

}


function toggleHeader() {
    if (isHeaderCollapsed) {
        // Remove opacity-0 class if it exists
        collapseHeaderItems.classList.remove("opacity-0")
        // Add opacity-100 class
        collapseHeaderItems.classList.add("opacity-100")
        // Set inline opacity style as fallback for better control
        collapseHeaderItems.style.opacity = "1"
        collapseHeaderItems.style.width = "60vw"
        collapseBtn.classList.remove("bi-list")
        collapseBtn.classList.add("bi-x", "max-lg:tw-fixed")
        isHeaderCollapsed = false

        setTimeout(() => window.addEventListener("click", onHeaderClickOutside), 1)

    } else {
        collapseHeaderItems.classList.remove("opacity-100")
        collapseHeaderItems.classList.add("opacity-0")
        // Set inline opacity style
        collapseHeaderItems.style.opacity = "0"
        collapseHeaderItems.style.width = "0vw"
        collapseBtn.classList.remove("bi-x", "max-lg:tw-fixed")
        collapseBtn.classList.add("bi-list")
        isHeaderCollapsed = true
        window.removeEventListener("click", onHeaderClickOutside)

    }
}

function responsive() {
    if (window.innerWidth > RESPONSIVE_WIDTH) {
        // Desktop view: reset all mobile menu styles
        collapseHeaderItems.style.width = ""
        collapseHeaderItems.style.opacity = ""
        collapseHeaderItems.classList.remove("opacity-0", "opacity-100")
        isHeaderCollapsed = false
        // Remove click outside listener if it exists
        window.removeEventListener("click", onHeaderClickOutside)
        // Reset button icon
        collapseBtn.classList.remove("bi-x", "max-lg:tw-fixed")
        collapseBtn.classList.add("bi-list")
    } else {
        // Mobile view: ensure menu is collapsed
        if (!isHeaderCollapsed) {
            // If menu was open, close it
            collapseHeaderItems.classList.remove("opacity-100")
            collapseHeaderItems.classList.add("opacity-0")
            collapseHeaderItems.style.opacity = "0"
            collapseHeaderItems.style.width = "0vw"
            collapseBtn.classList.remove("bi-x", "max-lg:tw-fixed")
            collapseBtn.classList.add("bi-list")
        }
        isHeaderCollapsed = true
        window.removeEventListener("click", onHeaderClickOutside)
    }
}

window.addEventListener("resize", responsive)


/**
 * Animations
 */

gsap.registerPlugin(ScrollTrigger)


gsap.to(".reveal-up", {
    opacity: 0,
    y: "100%",
})

gsap.to("#dashboard", {
    boxShadow: "0px 15px 25px -5px #7e22ceaa",
    duration: 0.3,
    scrollTrigger: {
        trigger: "#hero-section",
        start: "60% 60%",
        end: "80% 80%",
        // markers: true
    }

})

// straightens the slanting image
gsap.to("#dashboard", {

    scale: 1,
    translateY: 0,
    // translateY: "0%",
    rotateX: "0deg",
    scrollTrigger: {
        trigger: "#hero-section",
        start: window.innerWidth > RESPONSIVE_WIDTH ? "top 95%" : "top 70%",
        end: "bottom bottom",
        scrub: 1,
        // markers: true,
    }

})

const faqAccordion = document.querySelectorAll('.faq-accordion')

faqAccordion.forEach(function (btn) {
    btn.addEventListener('click', function () {
        this.classList.toggle('active')

        // Toggle 'rotate' class to rotate the arrow
        let content = this.nextElementSibling
        
        // content.classList.toggle('!tw-hidden')
        if (content.style.maxHeight === '200px') {
            content.style.maxHeight = '0px'
            content.style.padding = '0px 18px'

        } else {
            content.style.maxHeight = '200px'
            content.style.padding = '20px 18px'
        }
    })
})



// ------------- reveal section animations ---------------

const sections = gsap.utils.toArray("section")

sections.forEach((sec) => {

    const revealUptimeline = gsap.timeline({paused: true, 
                                            scrollTrigger: {
                                                            trigger: sec,
                                                            start: "10% 80%", // top of trigger hits the top of viewport
                                                            end: "20% 90%",
                                                            // markers: true,
                                                            // scrub: 1,
                                                        }})

    revealUptimeline.to(sec.querySelectorAll(".reveal-up"), {
        opacity: 1,
        duration: 0.8,
        y: "0%",
        stagger: 0.2,
    })


})
