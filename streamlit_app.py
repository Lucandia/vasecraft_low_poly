# Import libraries
import cadquery as cq
from uuid import uuid4
from math import cos, sin, sqrt, pi
import streamlit as st
import os
import time

def stl_preview(color, render):
    # Load and embed the JavaScript file
    with open("js/three.min.js", "r") as js_file:
        three_js = js_file.read()

    with open("js/STLLoader.js", "r") as js_file:
        stl_loader = js_file.read()

    with open("js/OrbitControls.js", "r") as js_file:
        orbital_controls = js_file.read()

    with open("js/stl-viewer.js", "r") as js_file:
        stl_viewer_component = (
            js_file.read()
            .replace('{__REPLACE_COLOR__}',f'0x{color[1:]}')
            .replace('{__REPLACE_MATERIAL__}',render)
        )

    session_id = st.session_state['session_id']
    st.components.v1.html(
        r'<div style="height:500px">'+
        r'<script>'+
        three_js+' '+
        stl_loader+' '+
        orbital_controls+' '+
        'console.log(\'frizzle\');'+
        stl_viewer_component+' '+
        r'</script>'+
        r'<stl-viewer model="./model'+'.stl'+r'"></stl-viewer>'+
        r'</div>',
        height = 500
    )

# def stl_preview(color):
#     ## Initialize pyvista reader and plotter
#     reader = pv.STLReader('vase.stl')
#     plotter = pv.Plotter(
#         border=True,
#         window_size=[580,400]) 
#     plotter.background_color = "white"

#     ## Read data and send to plotter
#     mesh = reader.read()
#     plotter.add_mesh(mesh,color=color)

#     ## Export to an external pythreejs
#     model_html = "model.html"
#     plotter.export_html(model_html)

#     ## Read the exported model
#     with open(model_html,'r') as file: 
#         model = file.read()

#     ## Show in webpage
#     st.components.v1.html(model,height=500)


if __name__ == "__main__":
    # initialize session id
    if "session_id" not in st.session_state:
        st.session_state['session_id'] = uuid4()
    session_id = st.session_state['session_id']


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
        tilt_res = st.slider('Tilt of each block', -r+1, r, step=1, value=r//10) # add a tilt to each block

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

        ### Cadquery file generation

    if concave:
        sides *= 2
    xy_angle = 360 / sides
    blocks = int(height/res)
    twist_block = twist/blocks
    tilt_block = tilt/blocks
    dim = [r+tilt_block*i+tilt_res*(i%2) for i in range(blocks+1)]
        
    rt_twist = 0
    for i in range(blocks):
        if concave:
            r_arr1 = [dim[i], dim[i]*concave_perc/100]
            r_arr2 = [dim[i+1], dim[i+1]*concave_perc/100]
        else:
            r_arr1 = [dim[i], dim[i]]
            r_arr2 = [dim[i+1], dim[i+1]]
        ps1 = [[cos(xy_angle*k*pi/180)*r_arr1[k%2], sin(xy_angle*k*pi/180)*r_arr1[k%2]] for k in range(sides)]
        s1 = cq.Sketch().polygon(ps1, angle=rt_twist)
        if not alternate_twist:
            rt_twist += twist_block
        else: 
            if i%2==0:
                rt_twist += twist_block
            else:
                rt_twist -= twist_block
        ps2 = [[cos(xy_angle*k*pi/180)*r_arr2[k%2], sin(xy_angle*k*pi/180)*r_arr2[k%2]] for k in range(sides)]
        s2 = cq.Sketch().polygon(ps2, angle=rt_twist)

        if i==0:
            result = (
                cq.Workplane()
                .placeSketch(s1, s2.moved(cq.Location(cq.Vector(0, 0, res))))
                .loft()
                )
        else:
            result = (result.
                    faces(">Z")
                    .workplane()
                    .placeSketch(s1, s2.moved(cq.Location(cq.Vector(0, 0, res))))
                    .loft()
                            )
    
    cq.exporters.export(result, 'model.stl')
    cq.exporters.export(result, f"vase.{out}")

        ### END CADQUERY PART

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
            render = st.selectbox(f"Render", ["material", "wireframe"], label_visibility="collapsed", key="model_render")
        with col2:
            color = st.color_picker('Model Color', '#505050', key="model_color")
        stl_preview(color, render)