mojo({
    base: {
        themes: {
            default: {
                primary: "#009DE0",
                secondary: "#E9F7FD",
                grey1: "#F6F6F6",
                grey2: "#EDEEEE",
                grey3: "#E4E4E4",
                grey4: "#717173",
                voltBlack: "#141414",
                
            }
        },
        fonts: {
            default: ["Nunito", "sans-serif"],
        },
    },
    patterns: {
            "body":{
                idle : "h-full d-flex flex-col",
            },
            "main": {
                idle : "mx-8 text-c-voltBlack flex-(1)",
                xl : "mx-16"
            },
            "input": {
                idle : "border border-1 border-c-gray:+25 px-2 rounded-4 h-10 outline-none"
            },
            "button": {
                idle : "px-4 rounded-sm h-10 outline-none bg-c-primary text-c-white",
                hover : "bg-c-#1FA9E4 cursor-pointer"
            },
            "img": {
                idle : "max-w-100%"
            },
            "h1": {
                idle : "text-w-black text-200",
                md : "text-250",
            },   
            "h2": {
                idle : "text-w-bold text-150",
                md : "text-170",
            },  
            "h3": {
                idle : "text-w-bold"
            },       
        },
    utilities: [
        {
            name: "light-btn",
            pattern: "bg-c-secondary text-c-primary"
        },
        {
            name: "rounded-btn",
            pattern: "rounded-full bg-c-secondary text-c-primary"
        },
        {
            name: "profile-btn",
            pattern: "bg-c-grey2 text-c-black rounded-full d-flex gap-2 j-content-center a-items-center pl-1"
        },
        {
            name: "tab-btn",
            pattern: "d-flex j-content-center a-items-center gap-2 px-4 founded-full text-c-grey4 cursor-pointer",
        },
        {
            name: "tab_secondary-btn",
            pattern: "text-120 text-c-black"
        },
        {
            name: "active",
            pattern: "bg-c-primary text-c-white rounded-full"
        },
        {
            name: "active_secondary",
            pattern: "border-b-3 border-c-black",
        },
        {
            name: "active_secondary_sm",
            pattern: "text-w-semibold",
        },
        {
            name: "bg-customer-hero",
            pattern: "background-image: url('/static/img/hero.jpg'); background-size: cover; background-repeat: no-repeat;"
        },
        {
            name: "overlay",
            body: "background: linear-gradient(to bottom, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.7));"
        },
        
    ]
})