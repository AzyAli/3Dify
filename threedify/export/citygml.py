"""
CityGML exporter for 3D building models.
This module provides functionality for exporting 3D building models to CityGML format.
This one took me a very long time to figure out but this is the best i could do with the time i had.
"""

import os
import logging
from typing import Any, Dict, Optional, Union
from pathlib import Path
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import numpy as np

from threedify.export.base import BaseExporter

logger = logging.getLogger(__name__)

class CityGMLExporter(BaseExporter):
    """Exporter for CityGML format."""
    
    def export(self, model_data: Any, output_path: Union[str, Path], **kwargs) -> Path:
        """Export model data to CityGML format.
        Args:
            model_data: Model data to export
            output_path (str or Path): Path to save the output file
            **kwargs: Additional parameters
                - lod (int): Level of detail (1-4)
                - building_attributes (dict): Additional building attributes
                - epsg (int): EPSG code for coordinate reference system
                - building_type (str): Type of building (residential, commercial, etc.)      
        Returns:
            Path: Path to the exported file
        """
        output_path = Path(output_path)
        if output_path.suffix.lower() != '.gml':
            output_path = output_path.with_suffix('.gml')
        logger.info(f"Exporting model to CityGML format: {output_path}")
        lod = kwargs.get('lod', 2)
        building_attributes = kwargs.get('building_attributes', {})
        epsg = kwargs.get('epsg', 4326)  # Default to WGS84
        building_type = kwargs.get('building_type', 'Building')
        os.makedirs(output_path.parent, exist_ok=True)
        
        try:
            root = self._create_citygml_root(epsg)
            self._add_building(root, model_data, lod, building_attributes, building_type)
            tree = ET.ElementTree(root)
            xml_str = ET.tostring(root, encoding='utf-8')
            dom = minidom.parseString(xml_str)
            pretty_xml = dom.toprettyxml(indent="  ")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(pretty_xml)
            logger.info(f"Model exported successfully to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to export model to CityGML: {str(e)}")
            raise
    
    def _create_citygml_root(self, epsg=4326):
        """Create the root element for a CityGML document.
        Args:
            epsg (int): EPSG code for coordinate reference system  
        Returns:
            ET.Element: Root element
        """
        nsmap = {
            'xmlns': 'http://www.opengis.net/citygml/2.0',
            'xmlns:core': 'http://www.opengis.net/citygml/2.0',
            'xmlns:bldg': 'http://www.opengis.net/citygml/building/2.0',
            'xmlns:gml': 'http://www.opengis.net/gml',
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xmlns:xAL': 'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0',
            'xsi:schemaLocation': 'http://www.opengis.net/citygml/2.0 http://schemas.opengis.net/citygml/2.0/cityGMLBase.xsd http://www.opengis.net/citygml/building/2.0 http://schemas.opengis.net/citygml/building/2.0/building.xsd'
        }
        root = ET.Element('CityModel')

        for ns_key, ns_val in nsmap.items():
            root.set(ns_key, ns_val)
        bounded_by = ET.SubElement(root, 'gml:boundedBy')
        envelope = ET.SubElement(bounded_by, 'gml:Envelope')
        envelope.set('srsName', f"EPSG:{epsg}")
        lower_corner = ET.SubElement(envelope, 'gml:lowerCorner')
        lower_corner.text = "-180.0 -90.0 0.0"
        upper_corner = ET.SubElement(envelope, 'gml:upperCorner')
        upper_corner.text = "180.0 90.0 100.0"
        return root
    
    def _add_building(self, root, model_data, lod, building_attributes, building_type):
        """Add a building to the CityGML document.
        Args:
            root (ET.Element): Root element
            model_data: Model data
            lod (int): Level of detail
            building_attributes (dict): Additional building attributes
            building_type (str): Type of building
        """
        city_object_member = ET.SubElement(root, 'cityObjectMember')
        building = ET.SubElement(city_object_member, f'bldg:{building_type}')
        building.set('gml:id', f'Building_{self._generate_uuid()}')
        if 'class' in building_attributes:
            class_elem = ET.SubElement(building, 'bldg:class')
            class_elem.text = building_attributes['class']
        if 'function' in building_attributes:
            function = ET.SubElement(building, 'bldg:function')
            function.text = building_attributes['function']
        if 'usage' in building_attributes:
            usage = ET.SubElement(building, 'bldg:usage')
            usage.text = building_attributes['usage']
        if 'year_of_construction' in building_attributes:
            year = ET.SubElement(building, 'bldg:yearOfConstruction')
            year.text = str(building_attributes['year_of_construction'])
        if 'storeys_above_ground' in building_attributes:
            storeys = ET.SubElement(building, 'bldg:storeysAboveGround')
            storeys.text = str(building_attributes['storeys_above_ground'])
        
        if 'storeys_below_ground' in building_attributes:
            storeys = ET.SubElement(building, 'bldg:storeysBelowGround')
            storeys.text = str(building_attributes['storeys_below_ground'])
        if 'measured_height' in building_attributes:
            height = ET.SubElement(building, 'bldg:measuredHeight')
            height.set('uom', 'm')
            height.text = str(building_attributes['measured_height'])
        if 'address' in building_attributes:
            addr = building_attributes['address']
            address = ET.SubElement(building, 'bldg:address')
            xal_address = ET.SubElement(address, 'xAL:Address')
            
            if 'country' in addr:
                country = ET.SubElement(xal_address, 'xAL:Country')
                country_name = ET.SubElement(country, 'xAL:CountryName')
                country_name.text = addr['country']
            if 'city' in addr:
                locality = ET.SubElement(xal_address, 'xAL:Locality')
                locality.set('Type', 'Town')
                locality_name = ET.SubElement(locality, 'xAL:LocalityName')
                locality_name.text = addr['city']
            if 'street' in addr:
                thoroughfare = ET.SubElement(xal_address, 'xAL:Thoroughfare')
                thoroughfare.set('Type', 'Street')
                thoroughfare_name = ET.SubElement(thoroughfare, 'xAL:ThoroughfareName')
                thoroughfare_name.text = addr['street']
                if 'number' in addr:
                    number = ET.SubElement(thoroughfare, 'xAL:ThoroughfareNumber')
                    number.text = addr['number']
            if 'postal_code' in addr:
                postal_code = ET.SubElement(xal_address, 'xAL:PostCode')
                postal_code_number = ET.SubElement(postal_code, 'xAL:PostCodeNumber')
                postal_code_number.text = addr['postal_code']
        if lod == 1:
            self._add_lod1_solid(building, model_data)
        elif lod == 2:
            self._add_lod2_solid(building, model_data)
        elif lod == 3:
            self._add_lod3_solid(building, model_data)
        elif lod == 4:
            self._add_lod4_solid(building, model_data)
        else:
            logger.warning(f"Invalid LOD: {lod}, using LOD2 instead")
            self._add_lod2_solid(building, model_data)
    
    def _add_lod1_solid(self, building, model_data):
        """Add a LOD1 solid (simple block model) to the building.
        Args:
            building (ET.Element): Building element
            model_data: Model data
        """
        lod1_solid = ET.SubElement(building, 'bldg:lod1Solid')
        solid = ET.SubElement(lod1_solid, 'gml:Solid')
        solid.set('gml:id', f'Solid_{self._generate_uuid()}')
        exterior = ET.SubElement(solid, 'gml:exterior')
        composite_surface = ET.SubElement(exterior, 'gml:CompositeSurface')
        geom = self._extract_geometry(model_data)
        if geom is None or len(geom) == 0:
            self._add_box_surfaces(composite_surface)
        else:
            self._add_simplified_building_surfaces(composite_surface, geom)
    
    def _add_lod2_solid(self, building, model_data):
        """Add a LOD2 solid (with roof shapes) to the building.
        Args:
            building (ET.Element): Building element
            model_data: Model data
        """
        lod2_solid = ET.SubElement(building, 'bldg:lod2Solid')
        solid = ET.SubElement(lod2_solid, 'gml:Solid')
        solid.set('gml:id', f'Solid_{self._generate_uuid()}')
        exterior = ET.SubElement(solid, 'gml:exterior')
        composite_surface = ET.SubElement(exterior, 'gml:CompositeSurface')
        geom = self._extract_geometry(model_data)
        if geom is None or len(geom) == 0:
            self._add_building_with_roof_surfaces(composite_surface)
        else:
            self._add_building_surfaces(composite_surface, geom)
    
    def _add_lod3_solid(self, building, model_data):
        """Add a LOD3 solid (with doors and windows) to the building.
        Args:
            building (ET.Element): Building element
            model_data: Model data
        """
        lod3_solid = ET.SubElement(building, 'bldg:lod3Solid')
        solid = ET.SubElement(lod3_solid, 'gml:Solid')
        solid.set('gml:id', f'Solid_{self._generate_uuid()}')
        exterior = ET.SubElement(solid, 'gml:exterior')
        composite_surface = ET.SubElement(exterior, 'gml:CompositeSurface')
        geom = self._extract_geometry(model_data)
        if geom is None or len(geom) == 0:
            self._add_detailed_building_surfaces(composite_surface)
        else:
            self._add_detailed_building_surfaces_from_geometry(composite_surface, geom)
    
    def _add_lod4_solid(self, building, model_data):
        """Add a LOD4 solid (with interior) to the building.
        Args:
            building (ET.Element): Building element
            model_data: Model data
        """
        lod4_solid = ET.SubElement(building, 'bldg:lod4Solid')
        solid = ET.SubElement(lod4_solid, 'gml:Solid')
        solid.set('gml:id', f'Solid_{self._generate_uuid()}')
        exterior = ET.SubElement(solid, 'gml:exterior')
        composite_surface = ET.SubElement(exterior, 'gml:CompositeSurface')
        geom = self._extract_geometry(model_data)
        if geom is None or len(geom) == 0:
            self._add_detailed_building_surfaces(composite_surface)
        else:
            self._add_detailed_building_surfaces_from_geometry(composite_surface, geom)
        self._add_interior_features(building, model_data)
    
    def _extract_geometry(self, model_data):
        """Extract geometry data from model_data.
        Args:
            model_data: Model data
        Returns:
            dict: Geometry data or None if not available
        """
        geom = {}
        if hasattr(model_data, 'mesh') and model_data.mesh:
            geom['vertices'] = model_data.mesh.get('vertices', None)
            geom['faces'] = model_data.mesh.get('faces', None)
            return geom
        elif hasattr(model_data, 'vertices') and hasattr(model_data, 'faces'):
            geom['vertices'] = model_data.vertices
            geom['faces'] = model_data.faces
            return geom
        elif (hasattr(model_data, 'building_segments') and 
              model_data.building_segments and 
              'contours' in model_data.building_segments):
            geom['contours'] = model_data.building_segments['contours']
            geom['building_data'] = model_data.building_segments
            return geom
        return None
    
    def _add_box_surfaces(self, composite_surface):
        """Add box surfaces to the composite surface.
        Args:
            composite_surface (ET.Element): CompositeSurface element
        """
        coords = [
            # Bottom face
            [(0, 0, 0), (10, 0, 0), (10, 10, 0), (0, 10, 0)],
            # Top face
            [(0, 0, 5), (10, 0, 5), (10, 10, 5), (0, 10, 5)],
            # Front face
            [(0, 0, 0), (10, 0, 0), (10, 0, 5), (0, 0, 5)],
            # Back face
            [(0, 10, 0), (10, 10, 0), (10, 10, 5), (0, 10, 5)],
            # Left face
            [(0, 0, 0), (0, 10, 0), (0, 10, 5), (0, 0, 5)],
            # Right face
            [(10, 0, 0), (10, 10, 0), (10, 10, 5), (10, 0, 5)]
        ]
        for i, face_coords in enumerate(coords):
            self._add_polygon_surface(composite_surface, face_coords, f'Box_Polygon_{i+1}')
    
    def _add_simplified_building_surfaces(self, composite_surface, geom):
        """Add simplified building surfaces to the composite surface.
        Args:
            composite_surface (ET.Element): CompositeSurface element
            geom (dict): Geometry data
        """
        if 'vertices' in geom and 'faces' in geom and geom['vertices'] is not None and geom['faces'] is not None:
            vertices = geom['vertices']
            faces = geom['faces']
            for i, face in enumerate(faces):
                face_coords = [vertices[idx] for idx in face]
                self._add_polygon_surface(composite_surface, face_coords, f'Building_Polygon_{i+1}')
        else:
            self._add_box_surfaces(composite_surface)
    
    def _add_building_with_roof_surfaces(self, composite_surface):
        """Add building surfaces with a roof to the composite surface.
        Args:
            composite_surface (ET.Element): CompositeSurface element
        """
        coords = [
            # Bottom face
            [(0, 0, 0), (10, 0, 0), (10, 10, 0), (0, 10, 0)],
            # Front face
            [(0, 0, 0), (10, 0, 0), (10, 0, 5), (5, 0, 8), (0, 0, 5)],
            # Back face
            [(0, 10, 0), (10, 10, 0), (10, 10, 5), (5, 10, 8), (0, 10, 5)],
            # Left face
            [(0, 0, 0), (0, 10, 0), (0, 10, 5), (0, 0, 5)],
            # Right face
            [(10, 0, 0), (10, 10, 0), (10, 10, 5), (10, 0, 5)],
            # Roof left
            [(0, 0, 5), (5, 0, 8), (5, 10, 8), (0, 10, 5)],
            # Roof right
            [(5, 0, 8), (10, 0, 5), (10, 10, 5), (5, 10, 8)]
        ]
        for i, face_coords in enumerate(coords):
            self._add_polygon_surface(composite_surface, face_coords, f'Building_Polygon_{i+1}')
    
    def _add_building_surfaces(self, composite_surface, geom):
        """Add building surfaces with roof from geometry to the composite surface.
        Args:
            composite_surface (ET.Element): CompositeSurface element
            geom (dict): Geometry data
        """
        if 'vertices' in geom and 'faces' in geom and geom['vertices'] is not None and geom['faces'] is not None:
            vertices = geom['vertices']
            faces = geom['faces']
            for i, face in enumerate(faces):
                face_coords = [vertices[idx] for idx in face]
                self._add_polygon_surface(composite_surface, face_coords, f'Building_Polygon_{i+1}')
        else:
            self._add_building_with_roof_surfaces(composite_surface)
    
    def _add_detailed_building_surfaces(self, composite_surface):
        """Add detailed building surfaces to the composite surface.
        Args:
            composite_surface (ET.Element): CompositeSurface element
        """
        self._add_building_with_roof_surfaces(composite_surface)
        window_coords = [(2, 0.01, 2), (4, 0.01, 2), (4, 0.01, 4), (2, 0.01, 4)]
        self._add_polygon_surface(composite_surface, window_coords, f'Window_Polygon_1')
        door_coords = [(7, 0.01, 0), (9, 0.01, 0), (9, 0.01, 3), (7, 0.01, 3)]
        self._add_polygon_surface(composite_surface, door_coords, f'Door_Polygon_1')
    
    def _add_detailed_building_surfaces_from_geometry(self, composite_surface, geom):
        """Add detailed building surfaces from geometry to the composite surface.
        Args:
            composite_surface (ET.Element): CompositeSurface element
            geom (dict): Geometry data
        """
        self._add_building_surfaces(composite_surface, geom)
        if 'building_data' in geom and 'openings' in geom['building_data']:
            openings = geom['building_data']['openings']
            
            for i, opening in enumerate(openings):
                if opening['type'] == 'window':
                    self._add_polygon_surface(composite_surface, opening['coords'], f'Window_Polygon_{i+1}')
                elif opening['type'] == 'door':
                    self._add_polygon_surface(composite_surface, opening['coords'], f'Door_Polygon_{i+1}')
    
    def _add_interior_features(self, building, model_data):
        """Add interior features to the building.
        Args:
            building (ET.Element): Building element
            model_data: Model data
        """
        room = ET.SubElement(building, 'bldg:Room')
        room.set('gml:id', f'Room_{self._generate_uuid()}')
        lod4_solid = ET.SubElement(room, 'bldg:lod4Solid')
        solid = ET.SubElement(lod4_solid, 'gml:Solid')
        solid.set('gml:id', f'Room_Solid_{self._generate_uuid()}')
        exterior = ET.SubElement(solid, 'gml:exterior')
        composite_surface = ET.SubElement(exterior, 'gml:CompositeSurface')
        coords = [
            # Bottom face
            [(2, 2, 0.1), (8, 2, 0.1), (8, 8, 0.1), (2, 8, 0.1)],
            # Top face
            [(2, 2, 4.9), (8, 2, 4.9), (8, 8, 4.9), (2, 8, 4.9)],
            # Front face
            [(2, 2, 0.1), (8, 2, 0.1), (8, 2, 4.9), (2, 2, 4.9)],
            # Back face
            [(2, 8, 0.1), (8, 8, 0.1), (8, 8, 4.9), (2, 8, 4.9)],
            # Left face
            [(2, 2, 0.1), (2, 8, 0.1), (2, 8, 4.9), (2, 2, 4.9)],
            # Right face
            [(8, 2, 0.1), (8, 8, 0.1), (8, 8, 4.9), (8, 2, 4.9)]
        ]
        for i, face_coords in enumerate(coords):
            self._add_polygon_surface(composite_surface, face_coords, f'Room_Polygon_{i+1}')
    
    def _add_polygon_surface(self, composite_surface, coords, polygon_id):
        """Add a polygon surface to the composite surface.
        Args:
            composite_surface (ET.Element): CompositeSurface element
            coords (list): List of coordinates for the polygon
            polygon_id (str): ID for the polygon
        """
        surface_member = ET.SubElement(composite_surface, 'gml:surfaceMember')
        polygon = ET.SubElement(surface_member, 'gml:Polygon')
        polygon.set('gml:id', polygon_id)
        exterior = ET.SubElement(polygon, 'gml:exterior')
        linear_ring = ET.SubElement(exterior, 'gml:LinearRing')
        pos_list = ' '.join([f'{x} {y} {z}' for x, y, z in coords])
        pos_list_elem = ET.SubElement(linear_ring, 'gml:posList')
        pos_list_elem.text = pos_list
    
    def _generate_uuid(self):
        """Generate a unique ID for CityGML elements.
        Returns:
            str: Unique ID
        """
        import uuid
        return uuid.uuid4().hex
    
    @property
    def name(self) -> str:
        """Get the name of the exporter.
        Returns:
            str: Exporter name
        """
        return "citygml"
    
    @property
    def extension(self) -> str:
        """Get the file extension for this exporter.
        Returns:
            str: File extension (without dot)
        """
        return "gml"
