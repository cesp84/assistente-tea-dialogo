document.getElementById("chat-form").addEventListener("submit", async function (event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);
    const respostaElemento = document.getElementById("resposta");

    respostaElemento.innerText = "Processando...";

    const response = await fetch("enviar/", {
        method: "POST",
        body: formData,
        headers: {
            "X-CSRFToken": formData.get("csrfmiddlewaretoken")
        }
    });

    const data = await response.json();

    respostaElemento.innerText = data.resposta;
});