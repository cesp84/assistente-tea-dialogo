document.getElementById("chat-form").addEventListener("submit", async function (event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);
    const respostaElemento = document.getElementById("resposta");
    const mensagemElemento = document.getElementById("mensagem");
    const submitButton = form.querySelector('button[type="submit"]');

    // Desabilita botão e mostra estado de carregamento
    submitButton.disabled = true;
    respostaElemento.innerText = "Processando...";

    try {
        const response = await fetch("/assistente_tea/enviar/", {
            method: "POST",
            body: formData,
            headers: {
                "X-CSRFToken": formData.get("csrfmiddlewaretoken")
            }
        });

        if (!response.ok) {
            throw new Error(`Erro HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();

        if (data && data.resposta) {
            respostaElemento.innerText = data.resposta;
        } else {
            respostaElemento.innerText = "Resposta vazia ou malformada.";
        }

    } catch (error) {
        console.error("Erro na comunicação:", error);
        respostaElemento.innerText = `Falha ao processar: ${error.message}`;
    } finally {
        // Reabilita botão e foca no campo
        submitButton.disabled = false;
        mensagemElemento.value = "";
        mensagemElemento.focus();
    }
});