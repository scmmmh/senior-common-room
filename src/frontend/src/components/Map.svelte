<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import { useNavigate, useParams } from 'svelte-navigator';
    import * as Phaser from 'phaser';

    import { rooms, badges, action, executeAction, user, sendMessage, messages } from '../store';
    import AvatarList from './AvatarList.svelte';

    interface LayerProperty {
        name: string;
        value: string | number | boolean;
    }
    interface LayerPropertyDict {
        [x: string]: string | number | boolean;
    }

	const navigate = useNavigate();
    const params = useParams();
    let game = null;
    let navTargetLayer = null;
    let lastScene = null;
    let avatarList = [];
    let myX = 0;
    let myY = 0;
    let canvas = null as HTMLCanvasElement;

    class Avatar {

        public x: number;
        public y: number;
        private scene: Phaser.Scene;
        private user: UpdateAvatarLocationUserPayload;
        private face: Phaser.GameObjects.Image;
        private text: Phaser.GameObjects.Text;
        private outline: Phaser.GameObjects.Graphics;
        private badges: [number, number, Phaser.GameObjects.Image][];

        constructor(scene: Phaser.Scene, user: UpdateAvatarLocationUserPayload) {
            this.scene = scene;
            this.user = user;
            this.x = 0;
            this.y = 0;
        }

        preload() {
            if (!this.scene.textures.exists('user.' + this.user.id)) {
                this.scene.load.image('user.' + this.user.id, this.user.avatar + '-small.png');
            }
            $badges.forEach((badge) => {
                if (!this.scene.textures.exists('badge.' + badge.role)) {
                    this.scene.load.image('badge.' + badge.role, badge.url);
                }
            });
        }

        create() {
            this.face = this.scene.add.image(this.x * 48 + 24, this.y * 48 + 24, 'user.' + this.user.id);
            this.face.setDepth(1);
            this.text = this.scene.add.text(this.face.x, this.face.y + 28, this.user.name, { font: "14px Arial", fill: "#000" });
            this.text.setStroke('#fff', 3);
            this.text.setShadow(2, 2, "#333333", 2, true, true);
            this.text.setOrigin(0.5, 0);
            this.text.setDepth(1);
            this.outline = this.scene.add.graphics();
            this.outline.lineStyle(2, '0x374151', 1);
            this.outline.strokeCircle(0, 0, 24);
            this.outline.setDepth(1);
            this.outline.x = this.face.x;
            this.outline.y = this.face.y;
            this.badges = [];
            let badgeCount = 0;
            this.user.roles.forEach((role, idx) => {
                if ($badges.filter((badge) => { return badge.role === role; }).length > 0) {
                    if (badgeCount < 4) {
                        badgeCount = badgeCount + 1;
                        let offsetX = 0;
                        let offsetY = 0;
                        if (idx === 0) {
                            offsetX = 20;
                            offsetY = 20;
                        } else if (idx === 1) {
                            offsetX = -20;
                            offsetY = 20;
                        } else if (idx === 2) {
                            offsetX = -20;
                            offsetY = -20;
                        } else if (idx === 3) {
                            offsetX = 20;
                            offsetY = -20;
                        }
                        const badgeSprite = this.scene.add.image(this.face.x + offsetX, this.face.y + offsetY, 'badge.' + role);
                        badgeSprite.setDepth(1);
                        this.badges.push([offsetX, offsetY, badgeSprite]);
                    }
                }
            });
        }

        follow() {
            this.scene.cameras.main.startFollow(this.face, true, 1, 1);
        }

        move(x: number, y: number) {
            this.x = x;
            this.y = y;
            if (this.face) {
                this.face.x = this.x * 48 + 24;
                this.face.y = this.y * 48 + 24;
                if (this.text) {
                    this.text.x = this.face.x;
                    this.text.y = this.face.y + 28;
                }
                if (this.outline) {
                    this.outline.x = this.face.x;
                    this.outline.y = this.face.y;
                }
                this.badges.forEach(([offsetX, offsetY, badge]) => {
                    badge.x = this.face.x + offsetX;
                    badge.y = this.face.y + offsetY;
                });
            }
        }

        moveDelta(xDelta: number, yDelta: number) {
            this.move(this.x + xDelta, this.y + yDelta);
        }

        update(location: UpdateAvatarLocationPayload) {
            this.move(location.x, location.y);
        }

        bringToTop() {
            this.scene.children.bringToTop(this.face);
            this.scene.children.bringToTop(this.text);
            this.scene.children.bringToTop(this.outline);
            this.badges.forEach(([offsetX, offsetY, badge]) => {
                this.scene.children.bringToTop(badge);
            });
        }

        destroy() {
            this.face.destroy();
            this.text.destroy();
            this.outline.destroy();
            this.badges.forEach(([offsetX, offsetY, badge]) => {
                badge.destroy();
            });
        }
    }

    function createRoom(config: RoomConfigPayload) {
        class Scene extends Phaser.Scene {

            public map: Phaser.Tilemaps.Tilemap;
            private avatar: Avatar;
            public cursors;
            public layers = {};
            public layerProperties = {} as {[x: string]: LayerPropertyDict};
            private enterKey;
            private spaceKey;
            private avatars: {[x: number]: Avatar};
            private clickPoint = null;

            constructor () {
                super(config.slug);
                this.avatars = {}
            }

            init() {
                this.enterKey = this.input.keyboard.addKey('ENTER');
                this.spaceKey = this.input.keyboard.addKey('SPACE');
            }

            preload() {
                this.load.tilemapTiledJSON(config.slug + 'map', config.mapUrl);
                config.tilesets.forEach((tileset) => {
                    if (!this.textures.exists(tileset.name)) {
                        this.load.image(tileset.name, tileset.url);
                    }
                })
                this.avatar = new Avatar(this, {
                    id: $user.id,
                    avatar: $user.avatar,
                    name: $user.name,
                    roles: $user.roles,
                });
                this.avatar.preload();
            }

            create(data) {
                this.map = this.make.tilemap({ key: config.slug + 'map' });
                config.tilesets.forEach((tileset) => {
                    this.map.addTilesetImage(tileset.name, tileset.name);
                });
                this.map.getTileLayerNames().forEach((layerName) => {
                    this.layers[layerName] = this.map.createLayer(layerName, config.tilesets.map((tileset) => { return tileset.name; }));
                    const layer = this.map.getLayer(layerName);
                    this.layerProperties[layerName] = layer.properties.reduce((acc: LayerPropertyDict, val: LayerProperty) => {
                        if (val) {
                            acc[val.name] = val.value;
                        }
                        return acc;
                    }, {}) as LayerPropertyDict;
                });
                this.avatar.create();
                this.avatar.follow();
                this.avatar.bringToTop();
                this.updatePlayerLocation(data);
                this.updateAction(false);

                this.cursors = this.input.keyboard.createCursorKeys();
            }

            update(time, delta) {
                let xDelta = 0;
                let yDelta = 0;
                if (this.input.keyboard.checkDown(this.cursors.left, 100)) {
                    xDelta = -1;
                } else if (this.input.keyboard.checkDown(this.cursors.right, 100)) {
                    xDelta = 1;
                } else if (this.input.keyboard.checkDown(this.cursors.up, 100)) {
                    yDelta = -1;
                } else if (this.input.keyboard.checkDown(this.cursors.down, 100)) {
                    yDelta = 1;
                } else if ((this.input.keyboard.checkDown(this.enterKey, 500) || this.input.keyboard.checkDown(this.spaceKey)) && $action) {
                    executeAction.set($action);
                } else if (this.input.activePointer.buttons === 1 && this.input.activePointer.event.target === canvas) {
                    this.input.activePointer.updateWorldPoint(this.cameras.main);
                    this.clickPoint = this.layers[this.map.getTileLayerNames()[0]].worldToTileXY(this.input.activePointer.worldX, this.input.activePointer.worldY);
                } else if (this.input.activePointer.buttons === 0 && this.clickPoint !== null) {
                    action.set(null);
                    executeAction.set(null);
                    this.map.getTileLayerNames().forEach((layerName) => {
                        const tile = this.layers[layerName].getTileAt(this.clickPoint.x, this.clickPoint.y);
                        const layer = this.map.getLayer(layerName);
                        if (tile && layer && this.layerProperties[layerName] && this.layerProperties[layerName].action) {
                            const properties = this.layerProperties[layerName];
                            executeAction.set(properties);
                        }
                    });
                    this.clickPoint = null;
                }
                if (xDelta !== 0 || yDelta !== 0) {
                    const blocked = this.map.getTileLayerNames().map((layerName) => {
                        const tile = this.layers[layerName].getTileAtWorldXY(this.avatar.x * 48 + 24 + xDelta * 48, this.avatar.y * 48 + 24 + yDelta * 48);
                        const layer = this.map.getLayer(layerName);
                        if (tile && layer) {
                            if (tile.properties.collides || (this.layerProperties[layerName] && this.layerProperties[layerName].collides)) {
                                return true;
                            }
                        }
                        return false;
                    }).reduce((acc, val) => {
                        return acc || val;
                    }, false);
                    if (!blocked) {
                        this.avatar.moveDelta(xDelta, yDelta);
                        myX = this.avatar.x;
                        myY = this.avatar.y;

                        sendMessage({
                            type: 'set-avatar-location',
                            payload: {
                                room: config.slug,
                                x: this.avatar.x,
                                y: this.avatar.y
                            }
                        });
                        this.updateAction(true);
                    }
                }
            }

            updateAction(allowImmediate: boolean) {
                action.set(null);
                this.map.getTileLayerNames().forEach((layerName) => {
                    const tile = this.layers[layerName].getTileAtWorldXY(this.avatar.x * 48 + 24, this.avatar.y * 48 + 24);
                    const layer = this.map.getLayer(layerName);
                    if (tile && layer && this.layerProperties[layerName] && this.layerProperties[layerName].action) {
                        const properties = this.layerProperties[layerName];
                        if (properties.immediate && allowImmediate) {
                            if (properties.action === 'switchRoom') {
                                if (properties.targetLayer) {
                                    navTargetLayer = properties.targetLayer;
                                } else {
                                    navTargetLayer = null;
                                }
                                navigate('/room/' + properties.roomSlug);
                            }
                        } else {
                            action.set(properties);
                        }
                    }
                });
            }

            updatePlayerLocation(data) {
                if (this.map) {
                    if (data && data.from) {
                        const layer = this.map.getLayer(data.from);
                        if (layer) {
                            const coords = [];
                            const layer = this.map.getLayer(data.from);
                            for (let x = 0; x < layer.width; x++) {
                                for (let y = 0; y < layer.height; y++) {
                                    if (this.layers[layer.name].getTileAt(x, y)) {
                                        coords.push([x, y]);
                                    }
                                }
                            }
                            if (coords.length > 0) {
                                const playerCoords = coords[Math.floor(Math.random() * coords.length)];
                                this.avatar.move(playerCoords[0], playerCoords[1]);

                                sendMessage({
                                    type: 'set-avatar-location',
                                    payload: {
                                        room: config.slug,
                                        x: playerCoords[0],
                                        y: playerCoords[1],
                                    }
                                });
                            }
                        } else {
                            this.updatePlayerLocation(null);
                        }
                    } else {
                        const startLayerNames = this.map.getTileLayerNames().filter((layerName) => { return this.layerProperties[layerName].starting; })
                        if (startLayerNames.length > 0) {
                            this.updatePlayerLocation({from: startLayerNames[0]});
                        } else {
                            throw new Error('No starting layer specified');
                        }
                    }
                }
            }

            updateOtherAvatarLocation(data) {
                if (this.avatars[data.user.id]) {
                    this.avatars[data.user.id].move(data.x, data.y);
                } else {
                    this.avatars[data.user.id] = new Avatar(this, data.user);
                    this.avatars[data.user.id].preload();
                    this.load.once('complete', () => {
                        if (this.avatars[data.user.id]) {
                            this.avatars[data.user.id].create();
                            this.avatars[data.user.id].move(data.x, data.y);
                            this.avatar.bringToTop();
                        }
                    });
                    this.load.start();

                    sendMessage({
                        type: 'set-avatar-location',
                        payload: {
                            room: config.slug,
                            x: this.avatar.x,
                            y: this.avatar.y,
                        }
                    });
                }
            }

            removeOtherAvatar(data) {
                if (this.avatars[data.user] !== undefined) {
                    this.avatars[data.user].destroy();
                    delete this.avatars[data.user];
                }
            }

            clearOtherAvatars() {
                Object.values(this.avatars).forEach((avatar) => {
                    avatar.destroy();
                });
                this.avatars = {};
            }
        }

        return Scene;
    }

    const phaserConfig = {
        type: Phaser.AUTO,
        backgroundColor: '#1F2937',
	    scale: {
            mode: Phaser.Scale.RESIZE,
            autoCenter: Phaser.Scale.CENTER_BOTH
        },
	    scene: [],
        parent: 'game',
    };

    onMount(() => {
        game = new Phaser.Game(phaserConfig);
        $rooms.forEach((roomConfig) => {
            game.scene.add(roomConfig.slug, createRoom(roomConfig), roomConfig.slug === $params.rid);
        });
        canvas = game.canvas;
        lastScene = $params.rid;
        sendMessage({
            type: 'enter-room',
            payload: {
                room: $params.rid
            }
        });
    });

    const unsubscribeParams = params.subscribe((params) => {
        if (game) {
            if (lastScene && game.scene.getScene(lastScene)) {
                game.scene.getScene(lastScene).sys.setVisible(false);
                game.scene.pause(lastScene);
                sendMessage({
                    type: 'leave-room',
                    payload: {
                        room: lastScene,
                    }
                });
                game.scene.getScene(lastScene).clearOtherAvatars();
            }
            if (game.scene.getScene(params.rid)) {
                sendMessage({
                    type: 'enter-room',
                    payload: {
                        room: params.rid,
                    }
                });
                game.scene.getScene(params.rid).events.once(Phaser.Scenes.Events.RESUME, () => {
                    game.scene.getScene(params.rid).updatePlayerLocation({ from: navTargetLayer });
                });
                game.scene.run(params.rid, { from: navTargetLayer });
                game.scene.getScene(params.rid).sys.setVisible(true);
                lastScene = params.rid;
            }
        }
    });

    const unsubscribeMessages = messages.subscribe((message) => {
        if (message.type === 'update-avatar-location') {
            if (game) {
                game.scene.getScene(lastScene).updateOtherAvatarLocation(message.payload);
            }
            let existIdx = null;
            let insertIdx = null;
            avatarList.forEach((avatar, idx) => {
                if (avatar.user.id === message.payload.user.id) {
                    existIdx = idx;
                }
                if (avatar.user.name >= message.payload.user.name) {
                    insertIdx = idx;
                }
            });
            if (existIdx !== null) {
                avatarList[existIdx] = message.payload;
            } else {
                if (insertIdx === null) {
                    avatarList.push(message.payload);
                } else {
                    avatarList.splice(insertIdx, 0, message.payload);
                }
            }
            avatarList = avatarList;
        } else if (message.type === 'remove-avatar') {
            if (game) {
                game.scene.getScene(lastScene).removeOtherAvatar(message.payload);
            }
            let removeIdx = -1;
            avatarList.forEach((avatar, idx) => {
                if (avatar.user.id === message.payload.user) {
                    removeIdx = idx;
                }
            });
            if (removeIdx >= 0) {
                avatarList.splice(removeIdx, 1);
                avatarList = avatarList;
            }
        }
    });

    onDestroy(() => {
        sendMessage({
            type: 'leave-room',
            payload: {
                room: lastScene,
            }
        });
        game.destroy(true);
        unsubscribeParams();
        unsubscribeMessages();
    });
</script>

<div id="game" class="flex-1"></div>
<AvatarList avatars={avatarList} x={myX} y={myY}/>
