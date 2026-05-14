FROM nginx:alpine

# Copiar los archivos estáticos al directorio de Nginx
COPY index.html /usr/share/nginx/html/index.html
COPY style.css  /usr/share/nginx/html/style.css
COPY app.js     /usr/share/nginx/html/app.js

# Puerto por defecto de Nginx
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
