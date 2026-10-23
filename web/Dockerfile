FROM nginx:1.27-alpine
# bust static asset cache on rebuild
ARG CACHEBUST=2026-10-23-opla-ui-v2
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY public/ /usr/share/nginx/html/
EXPOSE 3000
