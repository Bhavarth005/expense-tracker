let donut = document.querySelector(".donut");
let target_percent = 26;
let start = "50% 50%, 50% 0%";
let x_cor, y_cor;

// function update_percent(target_percent){
//     if(target_percent <= 12.5){
//         x_cor = (50 * target_percent) / 12.5;
//         donut.style.clipPath = `polygon(50% 50%, 50% 0, ${50 + x_cor}% 0)`;
//     }else if(target_percent <= 37.5){
//         y_cor = (100 * (target_percent - 12.5)) / 25;
//         donut.style.clipPath = `polygon(50% 50%, 50% 0, 100% 0, 100% ${y_cor}%)`;
//     }else if(target_percent <= 62.5){
//         x_cor = (100 * (target_percent - 37.5)) / 25;
//         donut.style.clipPath = `polygon(50% 50%, 50% 0, 100% 0, 100% 100%, ${100 - x_cor}% 100%)`;
//     }else if(target_percent <= 87.5){
//         y_cor = (100 * (target_percent - 62.5)) / 25;
//         donut.style.clipPath = `polygon(50% 50%, 50% 0, 100% 0, 100% 100%, 0 100%, 0 ${100 - y_cor}%)`;
//     }else{
//         x_cor = (50 * (target_percent - 87.5)) / 12.5
//         donut.style.clipPath = `polygon(50% 50%, 50% 0, 100% 0, 100% 100%, 0 100%, 0 0, ${x_cor}% 0)`;
//     }
// }

function get_clip_path(percent){
    if(percent <= 12.5){
        x_cor = (50 * percent) / 12.5;
        return `polygon(50% 50%, 50% 0, ${50 + x_cor}% 0)`;
    }else if(percent <= 37.5){
        y_cor = (100 * (percent - 12.5)) / 25;
        return `polygon(50% 50%, 50% 0, 100% 0, 100% ${y_cor}%)`;
    }else if(percent <= 62.5){
        x_cor = (100 * (percent - 37.5)) / 25;
        return `polygon(50% 50%, 50% 0, 100% 0, 100% 100%, ${100 - x_cor}% 100%)`;
    }else if(percent <= 87.5){
        y_cor = (100 * (percent - 62.5)) / 25;
        return `polygon(50% 50%, 50% 0, 100% 0, 100% 100%, 0 100%, 0 ${100 - y_cor}%)`;
    }else{
        x_cor = (50 * (percent - 87.5)) / 12.5
        return `polygon(50% 50%, 50% 0, 100% 0, 100% 100%, 0 100%, 0 0, ${x_cor}% 0)`;
    }
}
