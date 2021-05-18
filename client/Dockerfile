# Stage 0, "build-stage", based on Node.js, to build and compile the frontend
FROM node:12.18.4-alpine3.12 as build-stage
ENV current_work_dir=/usr/src/app/client/
WORKDIR ${current_work_dir}
COPY package*.json ${current_work_dir}
RUN npm install
COPY ./ ${current_work_dir}
RUN npm run build

# Stage 1, based on Nginx, to have only the compiled app, ready for production with Nginx
FROM nginx:1.18-alpine
COPY --from=build-stage /usr/src/app/client/build/ /usr/share/nginx/html
# Copy the default nginx.conf provided by tiangolo/node-frontend
COPY --from=build-stage /usr/src/app/client/nginx/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]