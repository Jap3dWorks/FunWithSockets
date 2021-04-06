const { Server } = require('net');

const server = new Server();

const BYTES = 4;
const MAX_SIZE = Math.pow(2, BYTES*8) - 1;

const options = {
    port: 8000,
    host: '0.0.0.0'
};

const users = new Map();

// FUNCTIONS //
function userName(name) {
    const randomColor = () => {
        const d = Math.random() > 0.5 ? '\x1b[1m' : '';
        const u = Math.round(Math.random()*5) + 31;
        return `${d}\x1b[${u}m`;
    };
    return randomColor() + name + '\x1b[0m';
}

function write(socket, message) {
    const msgSize = Buffer.byteLength(message, 'utf-8');
    const size = Math.min(msgSize, MAX_SIZE);

    const buffer = Buffer.alloc(BYTES + size);
    buffer.writeUInt32LE(size);
    buffer.write(message, BYTES, "utf-8"); 

    socket.write(buffer);
}

function alert(message, socket) {
    for(let s of users.keys()) {
        if (s !== socket) {
            write(s, message);
        }        
    }
}

function chat(user, message, socket) {
    for(let s of users.keys()) {
        if (s !== socket) {
            write(s, `${user}: ${message}`);
        }        
    }
}

// EVENTS //
server.on('connection', socket => {    

    users.set(socket, {});

    const remoteSocket = `${socket.remoteAddress}:${socket.remotePort}`;
    console.log(`New connection from ${remoteSocket}`);

    write(socket, 'Introduce tu nombre de usuario:');

    socket.on('data', buffer => {        
        const user = users.get(socket);
        if (user.message) {
            user.message += buffer.toString('utf-8');
        }
        else {
            user.total = buffer.readUInt32LE();    
            if (user.total > 0) {
                user.message = buffer.toString('utf-8', BYTES);
            }            
            else {
                const b = Buffer.alloc(BYTES);
                b.writeInt32LE(0);
                socket.write(b);     
                return;           
            }
        }

        if (user.message.length === user.total) {
            if (user.name) {
                console.log(`${remoteSocket} -> ${user.name}: ${user.message}`);
                chat(user.name, user.message);
            }
            else {
                user.name = userName(user.message);
                console.log(`${remoteSocket} -> New user: ${user.name}`);
                alert(`Bienvenido ${user.name}!`);
            }
            delete user.message;
        }
    });

    socket.on('error', console.error);

    socket.on('close', hasError => {
        const user = users.get(socket);
        users.delete(socket);
        console.log(`${remoteSocket} -> ${user.name} disconnected`);
        alert(`${user.name} se desconectó!`, socket); 
    });
});

server.listen(options, () => {
    console.log(`Server is listening on port ${options.port}`);
});

// PROCESS HANDLING // 
process.stdin.resume();

async function exitHandler(options, exitCode = 0) {    
    if (options.exit) {
        for(let s of users.keys()) {
            await s.end();            
        }
        server.close(err => {
            console.log(err ? 1 : exitCode);
            process.exit(err ? 1 : exitCode);
        })
    }
}

process.on('exit', exitHandler.bind(null,{cleanup:true}));
process.on('SIGINT', exitHandler.bind(null, {exit:true}));
process.on('SIGUSR1', exitHandler.bind(null, {exit:true}));
process.on('SIGUSR2', exitHandler.bind(null, {exit:true}));
process.on('uncaughtException', exitHandler.bind(null, {exit:true}));