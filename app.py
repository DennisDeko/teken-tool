# --- 3D EXPLODED VIEW (GEOPTIMALISEERD) ---
with c2:
    st.subheader("📦 3D Exploded View")
    fig3d = go.Figure()

    def add_box(fig, x_range, y_range, z_range, color, name, offset_x):
        x0, x1 = x_range[0] + offset_x, x_range[1] + offset_x
        fig.add_trace(go.Mesh3d(
            x=[x0, x1, x1, x0, x0, x1, x1, x0],
            y=[y_range[0], y_range[0], y_range[1], y_range[1], y_range[0], y_range[0], y_range[1], y_range[1]],
            z=[0, 0, 0, 0, h, h, h, h],
            i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2], 
            j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3], 
            k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
            color=color, flatshading=True, name=name, showscale=False, opacity=0.9
        ))

    for i in range(len(segs_x)-1):
        xs, xe = segs_x[i], segs_x[i+1]
        current_offset = i * spatiëring 
        c = cols[i % len(cols)]
        
        if vorm_type == "Steen":
            add_box(fig3d, (xs, xe), (0, l2), (0, h), c, f"Deel {i+1}", current_offset)
        else:
            add_box(fig3d, (xs, xe), (0, dikte_hoek), (0, h), c, f"Deel {i+1}", current_offset)
            if i == 0: 
                add_box(fig3d, (0, dikte_hoek), (dikte_hoek, l2), (0, h), c, "Poot", current_offset)

    # Vaste camera + Blokkeren van muis-interactie
    fig3d.update_layout(
        scene=dict(
            aspectmode='data',
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            camera=dict(eye=dict(x=1.8, y=1.8, z=1.2)),
            # HIER BLOKKEREN WE HET DRAAIEN:
            dragmode=False 
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        showlegend=False
    )

    # We gebruiken GEEN staticPlot, maar verbergen wel de knoppen
    st.plotly_chart(fig3d, use_container_width=True, config={'displayModeBar': False})
