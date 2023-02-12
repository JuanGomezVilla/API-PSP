class QuickFormSend {
    constructor(data){
        this.onClick = data.onClick;
        this.placeholder = data.placeholder;
        this.placeholderWait = data.placeholderWait;

        this.container = document.querySelector(data.selector);
        this.inputBox = document.createElement("input");
        this.inputBox.placeholder = data.placeholder;
        this.inputBox.style.marginRight = "5px";
        this.button = document.createElement("button");
        this.button.innerText = data.textButton;
        this.button.addEventListener("click", () => {
            this.onClick();
        });

        this.container.append(this.inputBox);
        this.container.append(this.button);
    }

    disabled(disable){
        this.button.disabled = disable;
        this.inputBox.disabled = disable;
        if(disable && this.placeholderWait != null) this.inputBox.placeholder = this.placeholderWait;
        else this.inputBox.placeholder = this.placeholder;
    }

    async sendGET(url, callback){
        let content = await fetch(url);
        callback(await content.json());
    }

    sendPOST(direccion, json, callback){
        var conexion = new XMLHttpRequest();
        conexion.open("POST", direccion, true);
        conexion.setRequestHeader("Content-Type", "application/json");
        conexion.onreadystatechange = function (){
            if(this.readyState != 4) return;
            if(this.status == 200) callback(JSON.parse(this.responseText));
        };
        conexion.send(JSON.stringify(json));
    }
}

class QuickJSON {
    constructor(data){
        this.container = document.querySelector(data.selector);
        this.json = data.json;
        this.code = document.createElement("code");
        this.pre = document.createElement("pre");
        this.pre.className = "codigoJSON";
        this.pre.append(this.code);
        this.container.append(this.pre);
        this.code.innerHTML = this.processJSON(this.json);
    }

    processJSON(datos){
        return JSON.stringify(datos, null, 4)
            .replace(/&/g, "&amp;")
            .replace(/\\"/g, "&quot;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/^( *)("[\w]+": )?("[^"]*"|[\w.+-]*)?([,[{])?$/gm, function (match, pIndent, pKey, pVal, pEnd){
                let textoClave = '<span class="json-key" style="color: brown">';
                let textoValor = '<span class="json-value" style="color: #ff7648">';
                let textoCadena = '<span class="json-string" style="color: olive">';
                let r = pIndent || "";
                if (pKey) r = r + textoClave + pKey.replace(/[": ]/g, "") + "</span>: ";
                if (pVal) r = r + (pVal[0] == '"' ? textoCadena : textoValor) + pVal + "</span>";
                return r + (pEnd || "");
            }
        );
    }
}