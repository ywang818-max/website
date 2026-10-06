from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parents[1]
x=np.linspace(1,50,600)
fig,ax=plt.subplots(figsize=(9,5.8))
for product,label,color in [(900,'Lower utility','#98a8ba'),(1250,'Highest attainable utility','#155ab6'),(1600,'Higher utility: unaffordable','#b85421')]:
 ax.plot(x,product/x,label=label,color=color,lw=2)
ax.plot([0,50],[100,0],color='#182335',lw=2,label='Budget: 2x + y = 100')
ax.scatter([25],[50],color='#155ab6',s=55,zorder=5)
ax.annotate('Best bundle: (25, 50)',xy=(25,50),xytext=(28,78),arrowprops={'arrowstyle':'-','color':'#155ab6'},fontsize=11)
ax.set(xlim=(0,52),ylim=(0,110),xlabel='Units of good x ($2 each)',ylabel='Units of good y ($1 each)')
ax.set_title('Why the best affordable bundle is a tangency',loc='left',weight='bold',pad=16)
ax.legend(loc='upper right',bbox_to_anchor=(1,-.16),frameon=False,ncol=2,fontsize=10)
ax.spines[['top','right']].set_visible(False);ax.grid(alpha=.2)
fig.subplots_adjust(bottom=.25)
fig.text(.12,.02,'Illustrative example: U = ln(x) + ln(y), budget = $100. Figure generated from the equations.',fontsize=9,color='#465265')
fig.savefig(root/'lagrange-intuition.png',dpi=180);plt.close(fig)
