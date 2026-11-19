const addInput = document.getElementById("addInput");
const addBtn = document.getElementById("addBtn");

addBtn.addEventListener("click", async function(){
    const title = addInput.value;
    try{
        const response = await fetch("/api/tasks", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                title: title,
                completed: false
            })
        })
        const data = await response.json();
        console.log(data);

    } catch (error) {
        console.log("Something went wrong:", error);
    }
});
async function get_task() {
    try{
        const response = await fetch("/api/tasks");
        const data = await response.json();
        console.log(data)
    } catch (error){
        console.log("something went wrong:",error);
    }

}
get_task();
