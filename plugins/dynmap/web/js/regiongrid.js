componentconstructors['regiongrid'] = function(dynmap, configuration) {
	// var cfg = $.extend({}, configuration);

	var me = this;

	this.chunkGroup = new L.LayerGroup();
	this.regionGroup = new L.LayerGroup();
	this.chunkMarkers = [];
	this.regionMarkers = [];

	this.chunkStyle = {
		color: '#800000',
		weight: '1',
		opacity: 0.6,
		clickable: false,
		fill: false
	};
	this.regionStyle = {
		color: '#000080',
		weight: '3',
		opacity: 0.6,
		clickable: false,
		fill: false
	};

	dynmap.addToLayerSelector(this.chunkGroup, 'Chunks', -1);
	dynmap.addToLayerSelector(this.regionGroup, 'Regions', -1);
	
	dynmap.map.on('moveend', function () {
		setTimeout(function () {updateGrid();}, 0);
	});

	dynmap.map.on('layeradd layerremove', function (event) {
		if (event.layer === me.chunkGroup || event.layer === me.regionGroup)
		{
			updateGrid();
		}
	});

	function updateGrid() {
		removeMarkers(me.chunkMarkers, me.chunkGroup);
		removeMarkers(me.regionMarkers, me.regionGroup);

		if (!dynmap.map.hasLayer(me.chunkGroup) && !dynmap.map.hasLayer(me.regionGroup))
		{
			return;
		}

		var minMax = getMinMaxData();

		addAreas(me.chunkGroup, me.chunkMarkers, me.chunkStyle, 16, minMax.minChunk, minMax.maxChunk);
		addAreas(me.regionGroup, me.regionMarkers, me.regionStyle, 16*32, minMax.minRegion, minMax.maxRegion);
	}

	function removeMarkers(markers, group) {
		while (markers.length) {
			group.removeLayer(markers.pop());
		}
	}

	function addAreas(group, markers, style, multiplier, min, max) {
		if (!dynmap.map.hasLayer(group)) return;
		if ((max.x - min.x) * (max.z - min.z) > 1500) return; // for performance reasons

		for (var x = min.x; x < max.x; x++) {
			for (var z = min.z; z < max.z; z++) {
				var pointList = [
					latlng(x * multiplier, 64, (z + 1) * multiplier),
					latlng((x + 1) * multiplier, 64, (z + 1) * multiplier),
					latlng((x + 1) * multiplier, 64, z * multiplier)
				];
				var marker = new L.Polyline(pointList, style);
				markers.push(marker);
				group.addLayer(marker);
			}
		}
	}

	function getMinMaxData() {
		// 0,0 => chunk 0 0 => region 0 0
		// 15, 15 => chunk 0 0 => region 0 0
		// 16, 16 => chunk 1 1 => region 0 0
		// 12228, 8898 => chunk 764 556 => region 23 17

		var bounds = dynmap.map.getBounds(),
			projection = dynmap.maptype.getProjection();

		var ne = projection.fromLatLngToLocation(bounds.getNorthEast(), 64),
			se = projection.fromLatLngToLocation(bounds.getSouthEast(), 64),
			sw = projection.fromLatLngToLocation(bounds.getSouthWest(), 64),
			nw = projection.fromLatLngToLocation(bounds.getNorthWest(), 64);

		var minX = Math.min(ne.x, se.x, sw.x, nw.x),
			maxX = Math.max(ne.x, se.x, sw.x, nw.x),
			minZ = Math.min(ne.z, se.z, sw.z, nw.z),
			maxZ = Math.max(ne.z, se.z, sw.z, nw.z),

			minChunk = {
				x: Math.floor(minX / 16) - 1,
				z: Math.floor(minZ / 16) - 1
			},
			maxChunk = {
				x: Math.ceil(maxX / 16) + 1,
				z: Math.ceil(maxZ / 16) + 1
			},

			minRegion = {
				x: Math.floor(minChunk.x / 32),
				z: Math.floor(minChunk.z / 32)
			},
			maxRegion = {
				x: Math.ceil(maxChunk.x / 32),
				z: Math.ceil(maxChunk.z / 32)
			};

		return {
			minChunk: minChunk,
			maxChunk: maxChunk,
			minRegion: minRegion,
			maxRegion: maxRegion
		};
	}
};