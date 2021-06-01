FROM openjdk

COPY minecraft_server.1.16.5.jar /minecraft/minecraft_server.1.16.5.jar

RUN adduser minecraft && \
    echo "eula=true" > /minecraft/eula.txt && \
    chown minecraft -R /minecraft

WORKDIR /minecraft
USER minecraft

CMD java -Xmx1024M -Xms1024M -jar minecraft_server.1.16.5.jar nogui