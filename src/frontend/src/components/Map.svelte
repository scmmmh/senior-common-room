<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import { useNavigate, useParams } from 'svelte-navigator';
    import * as Phaser from 'phaser';

    import { rooms, action, executeAction, user, sendMessage, messages } from '../store';

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

    function createRoom(config: RoomConfigPayload) {
        class Scene extends Phaser.Scene {

            public map: Phaser.Tilemaps.Tilemap;
            public player;
            public playerOutline;
            public playerText;
            public cursors;
            public layers = {};
            public layerProperties = {} as {[x: string]: LayerPropertyDict};
            private enterKey;
            private spaceKey;
            private avatars;

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
                    this.load.image(tileset.name, tileset.url);
                })
                this.load.image('face', $user.avatar + '-small.png');
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
                this.player = this.add.image(24, 24, 'face');
                this.playerText = this.add.text(this.player.x, this.player.y + 28, $user.name, { font: "14px Arial", fill: "#000" });
                this.playerText.setStroke('#fff', 3);
                this.playerText.setShadow(2, 2, "#333333", 2, true, true);
                this.playerText.setOrigin(0.5, 0);
                this.playerOutline = this.add.graphics();
                this.playerOutline.lineStyle(2, '0x374151', 1);
                this.playerOutline.strokeCircle(0, 0, 24);
                this.playerOutline.x = this.player.x;
                this.playerOutline.y = this.player.y;

                this.cursors = this.input.keyboard.createCursorKeys();

                this.cameras.main.startFollow(this.player, true, 1, 1);

                this.updatePlayerLocation(data);
            }

            update(time, delta) {
                let xDelta = 0;
                let yDelta = 0;
                if (this.input.keyboard.checkDown(this.cursors.left, 100) && this.player.x > 16) {
                    xDelta = -48;
                } else if (this.input.keyboard.checkDown(this.cursors.right, 100) && this.player.x < 1264) {
                    xDelta = 48;
                } else if (this.input.keyboard.checkDown(this.cursors.up, 100) && this.player.y > 16) {
                    yDelta = -48;
                } else if (this.input.keyboard.checkDown(this.cursors.down, 100) && this.player.y < 1264) {
                    yDelta = 48;
                } else if ((this.input.keyboard.checkDown(this.enterKey, 500) || this.input.keyboard.checkDown(this.spaceKey)) && $action) {
                    executeAction.set($action);
                }
                if (xDelta !== 0 || yDelta !== 0) {
                    const blocked = this.map.getTileLayerNames().map((layerName) => {
                        const tile = this.layers[layerName].getTileAtWorldXY(this.player.x + xDelta, this.player.y + yDelta);
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
                        this.player.x = this.player.x + xDelta;
                        this.player.y = this.player.y + yDelta;
                        this.playerOutline.x = this.player.x;
                        this.playerOutline.y = this.player.y;
                        this.playerText.x = this.player.x;
                        this.playerText.y = this.player.y + 28;

                        sendMessage({
                            type: 'set-avatar-location',
                            payload: {
                                room: config.slug,
                                x: (this.player.x - 24) / 48,
                                y: (this.player.y - 24) / 48,
                            }
                        });

                        action.set(null);
                        this.map.getTileLayerNames().forEach((layerName) => {
                            const tile = this.layers[layerName].getTileAtWorldXY(this.player.x, this.player.y);
                            const layer = this.map.getLayer(layerName);
                            if (tile && layer && this.layerProperties[layerName] && this.layerProperties[layerName].action) {
                                const properties = this.layerProperties[layerName];
                                if (properties.action === 'switchRoom' && properties.immediate) {
                                    if (properties.targetLayer) {
                                        navTargetLayer = properties.targetLayer;
                                    } else {
                                        navTargetLayer = null;
                                    }
                                    navigate('/room/' + properties.roomSlug);
                                } else {
                                    action.set(properties);
                                }
                            }
                        });
                    }
                }
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
                                this.player.x = playerCoords[0] * 48 + 24;
                                this.player.y = playerCoords[1] * 48 + 24;
                                this.playerOutline.x = this.player.x;
                                this.playerOutline.y = this.player.y;
                                this.playerText.x = this.player.x;
                                this.playerText.y = this.player.y + 28;

                                sendMessage({
                                    type: 'set-avatar-location',
                                    payload: {
                                        room: config.slug,
                                        x: (this.player.x - 24) / 48,
                                        y: (this.player.y - 24) / 48,
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
                    const parts = this.avatars[data.user.id];
                    if (parts.avatar && parts.outline && parts.text) {
                        parts.avatar.x = data.x * 48 + 24;
                        parts.avatar.y = data.y * 48 + 24;
                        parts.outline.x = data.x * 48 + 24;
                        parts.outline.y = data.y * 48 + 24;
                        parts.text.x = data.x * 48 + 24;
                        parts.text.y = data.y * 48 + 52;
                    }
                } else {
                    this.avatars[data.user.id] = {};
                    this.load.image('user.' + data.user.id, data.user.avatar + '-small.png');
                    this.load.once('complete', () => {
                        const parts = this.avatars[data.user.id];
                        if (parts !== undefined) {
                            parts.avatar = this.add.image(data.x * 48 + 24, data.y * 48 + 24, 'user.' + data.user.id);
                            parts.outline = this.add.graphics();
                            parts.outline.lineStyle(2, '0x374151', 1);
                            parts.outline.strokeCircle(0, 0, 24);
                            parts.outline.x = data.x * 48 + 24;
                            parts.outline.y = data.y * 48 + 24;
                            parts.text = this.add.text(data.x * 48 + 24, data.y * 48 + 52, data.user.name, { font: "14px Arial", fill: "#000" });
                            parts.text.setStroke('#fff', 3);
                            parts.text.setShadow(2, 2, "#333333", 2, true, true);
                            parts.text.setOrigin(0.5, 0);
                        }
                    });
                    this.load.start();

                    sendMessage({
                        type: 'set-avatar-location',
                        payload: {
                            room: config.slug,
                            x: (this.player.x - 24) / 48,
                            y: (this.player.y - 24) / 48,
                        }
                    });
                }
            }

            removeOtherAvatar(data) {
                console.log('Removing', data);
                if (this.avatars[data.user] !== undefined) {
                    const parts = this.avatars[data.user];
                    if (parts.avatar) {
                        parts.avatar.destroy();
                    }
                    if (parts.outline) {
                        parts.outline.destroy();
                    }
                    if (parts.text) {
                        parts.text.destroy();
                    }
                    delete this.avatars[data.user];
                }
            }

            clearOtherAvatars() {
                Object.values(this.avatars).forEach((avatar) => {
                    if (avatar.avatar) {
                        avatar.avatar.destroy();
                    }
                    if (avatar.outline) {
                        avatar.outline.destroy();
                    }
                    if (avatar.text) {
                        avatar.text.destroy();
                    }
                });
                this.avatars = {};
            }
        }

        return Scene;
    }

    const phaserConfig = {
        type: Phaser.AUTO,
        backgroundColor: '#222222',
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
        } else if (message.type === 'remove-avatar') {
            if (game) {
                game.scene.getScene(lastScene).removeOtherAvatar(message.payload);
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

<div id="game" class="v-full h-full"></div>
