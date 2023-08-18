# Import libraries
from build123d import *
from math import cos, sin, sqrt, pi
import streamlit as st
import os
import time
import base64

def render_svg(svg):
    """Renders the given svg string."""
    b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
    html = r'<img src="data:image/svg+xml;base64,%s"/>' % b64
    st.write(html, unsafe_allow_html=True)

if __name__ == "__main__":
    for file in os.listdir():
        if 'file' in file:
            try:
                os.remove(file)
            except:
                print(f'Cannot remove file {file}')

    st.title('VaseCraft: Low-Poly Vase Generator')
    st.write("Generate low-poly vases for 3D printing in vase mode.! If you like the project put a like on [Printables](https://www.printables.com/it/model/556002-vasecraft-low-poly-vase-generator) or [support me with a coffee](https://www.paypal.com/donate/?hosted_button_id=V4LJ3Z3B3KXRY)! On Printables you can find more info about the project.", unsafe_allow_html=True)

    # output file type
    _, _, col3, _, _ = st.columns(5)
    with col3:
        out = st.selectbox('Output file type', ['stl', 'step'])

    col1, col2, col3 = st.columns(3)
    with col1:
        height = st.slider('Height', 1, 300, step=1, value=100) # height of the vase
    with col2:
        r = st.slider('Radius', 1, 180, step=1, value=60) # radius of the vase
    with col3:
        sides = st.slider('N° sides', 1, 30, step=1, value=10) # number of sides

    col1, col2, col3 = st.columns(3)
    with col1:
        n_block = st.slider('N° blocks', 1, height//5, step=1, value=6) # number of blocks
        res = height/n_block # height of each block
    with col2:
        tilt = st.slider('Tilt', -r+1, r, step=1, value=r//5) # add a slope to the vase wall
    with col3:
        tilt_res = st.slider('Tilt of each block', -r, r, step=1, value=r//10) # add a tilt to each block

    col1, col2, col3 = st.columns(3)
    with col1:
        concave = st.checkbox('Concave shape') # make a concave shape (like a star)
    with col2:
        max_ang = int((sides-2)*180/sides)
        twist = st.slider('Twist', -max_ang, max_ang, step=1, value=max_ang//2) # twist angle of the vase
    with col3:
        alternate_twist = st.checkbox('Alternate twist') # alternate the twist

    if concave:
        _, col2, _ = st.columns(3)
        with col2:
            concave_perc = st.slider('Concave radius %', 0, 100, step=1, value=85) # the percentage radius of the concave shape

    start = time.time()
    with st.spinner('Wait for it...'):
        ### STARTBUILD123D PART: GENERATE THE MODEL
        if concave:
            sides *= 2
        xy_angle = 360 / sides
        blocks = int(height/res)
        twist_block = twist/blocks
        tilt_block = tilt/blocks
        dim = [r+tilt_block*i+tilt_res*(i%2) for i in range(blocks+1)]

        rt_twist = 0
        with BuildPart() as vase:
            for i in range(blocks):
                if concave:
                    r_arr1 = [dim[i], dim[i]*concave_perc/100]
                    r_arr2 = [dim[i+1], dim[i+1]*concave_perc/100]
                else:
                    r_arr1 = [dim[i], dim[i]]
                    r_arr2 = [dim[i+1], dim[i+1]]
                ps1 = [[cos(xy_angle*k*pi/180)*r_arr1[k%2], sin(xy_angle*k*pi/180)*r_arr1[k%2]] for k in range(sides)]
                ps2 = [[cos(xy_angle*k*pi/180)*r_arr2[k%2], sin(xy_angle*k*pi/180)*r_arr2[k%2]] for k in range(sides)]
                with BuildSketch(Plane.XY.offset(res*i).rotated((0,0,rt_twist))) as sk_bot:
                    Polygon(*ps1)
                if not alternate_twist:
                    rt_twist += twist_block
                else:
                    if i%2==0:
                        rt_twist += twist_block
                    else:
                        rt_twist -= twist_block
                with BuildSketch(Plane.XY.offset(res*(i+1)).rotated((0,0,rt_twist))) as sk_top:
                    Polygon(*ps2)
                loft()

        if out == 'stl':
            vase.part.export_stl('vase.stl')
        elif out == 'step':
            vase.part.export_step('vase.step')

        visible, hidden = vase.part.project_to_viewport((r*2, r*2, height/2))
        max_dimension = max(*Compound(children=visible + hidden).bounding_box().size)
        exporter = ExportSVG(scale= 50 / max_dimension)
        exporter.add_layer("Hidden", line_color=(200, 200, 200), line_type=LineType.DASHED, line_weight=0.25)
        exporter.add_layer("Visible", line_color=(50, 50, 50), line_weight=0.5)
        exporter.add_shape(hidden, layer="Hidden")
        exporter.add_shape(visible, layer="Visible")
        exporter.write("vase_side.svg")

        visible, hidden = vase.part.project_to_viewport((0, 0, height*2))
        max_dimension = max(*Compound(children=visible + hidden).bounding_box().size)
        exporter = ExportSVG(scale= 50 / max_dimension)
        exporter.add_layer("Hidden", line_color=(200, 200, 200), line_type=LineType.DASHED, line_weight=0.25)
        exporter.add_layer("Visible", line_color=(50, 50, 50), line_weight=0.5)
        exporter.add_shape(hidden, layer="Hidden")
        exporter.add_shape(visible, layer="Visible")
        exporter.write("vase_top.svg")

        ### END BUILD123D PART

    end = time.time()
    if f'vase.{out}' not in os.listdir():
        st.error('The program was not able to generate the mesh.', icon="🚨")
    else:
        st.success(f'Rendered in {int(end-start)} seconds', icon="✅")
        _, _, col3, _, _ = st.columns(5)
        with col3:
            with open(f'vase.{out}', "rb") as file:
                btn = st.download_button(
                        label=f"Download {out}",
                        data=file,
                        file_name=f'vase.{out}',
                        mime=f"model/{out}"
                    )
        st.markdown("Post the make [on Printables](https://www.printables.com/it/model/556002-vasecraft-low-poly-vase-generator) to support the project!", unsafe_allow_html=True)
        st.markdown("I am a student who enjoys 3D printing and programming. To support me with a coffee, just [click here!](https://www.paypal.com/donate/?hosted_button_id=V4LJ3Z3B3KXRY)", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.write("Vase side:")
            with open('vase_side.svg', 'r') as f:
                render_svg(f.read())
        with col2:
            st.write("Vase top:")
            with open('vase_top.svg', 'r') as f:
                render_svg(f.read())

