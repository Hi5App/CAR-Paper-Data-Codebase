import matplotlib.pyplot as plt

# Define square colors
color1 = 'royalblue'
color2 = 'c'
color3 = 'plum'
color4 = 'lightgreen'
# color4 = 'grey'

plt.rcParams['font.family'] = 'Helvetica'
# Set the square size and gap
square_size = 0.8
gap = 0.2

# Create a plot
fig, ax = plt.subplots(figsize = (6,8))

# Remove axes
ax.axis('off')

# Draw squares
for row in range(7):
    for col in range(9):
        if row >= 3:
            color = color1
        elif row == 2 and col < 2:
            color = color1
        elif row == 2 and col == 2:
            color = color2
        elif row == 2 and col <= 6 and col >= 3:
            color = color3
        elif row == 2 and col == 7:
            color = color4
        elif row == 0 or row == 1:
            color = color4

        x = col * (square_size + gap)
        y = row * (square_size + gap)
        rect = plt.Rectangle((x, y), square_size, square_size, color=color)
        ax.add_patch(rect)

# Set plot parameters
ax.set_aspect('equal')
ax.set_xlim(0, 8 * (square_size + gap) - gap)
ax.set_ylim(0, 8 * (square_size + gap) - gap)

# Create a custom legend
legend_elements = [
    plt.Rectangle((0, 0), 1, 1, color=color1, label='Full Coverage'),
    plt.Rectangle((0, 0), 1, 1, color=color2, label='Partial Coverage'),
    plt.Rectangle((0, 0), 1, 1, color=color3, label='Zero Coverage'),
    plt.Rectangle((0, 0), 1, 1, color=color4, label='Image Without Missing Point')
]
ax.legend(handles=legend_elements, loc='lower left', bbox_to_anchor=(-0.02, -0.15), ncol=2)

fig.text(0.5, 0.75, 'Missing Points Coverage in Dendrite Images(Threshold: 20)', ha='center', fontsize=12)
# Show the plot
plt.show()
