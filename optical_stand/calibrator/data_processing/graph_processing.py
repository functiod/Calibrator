class GraphProcessing():
    "Class for ease of working with graph objects"
    def __init__(self) -> None:
        pass

    def init_graph(self) -> None:
        '''Inits a real time graph'''
        self.ax.set_rticks([250, 300, 350, 400])
        self.ax.set_rlabel_position(-22.5)
        self.ax.grid(True)
        self.ax.set_title('Intensity to azimuth angle')

        plt.show(block=False)

    def update_plot(self, new_data: list) -> None:
        '''Updates a real time graph with new dotes'''
        x_new_data: list = new_data[self.xSensCol]
        y_new_data: list = new_data[self.ySensCol]
        self.ax.plot(x_new_data, y_new_data, '.')

        plt.draw()
        plt.pause(0.01)

    def plotAproxPolynom(self, buffer: list | None = None, from_file: str = '') -> None:
        if from_file != '':
            mybuffer: list = self.downloadFile(from_file)
        else:
            mybuffer: list = buffer
        npbuffer: np.ndarray = np.array(mybuffer)
        coefs: list = self.defineAproxPolynom(npbuffer)
        x: list = npbuffer[:, self.radiusSensCol]
        y: list = npbuffer[:, self.zenRotatorCol]
        polynomial = np.poly1d(np.flip(coefs))
        xnew: list = np.linspace(0, 200, 200)
        ynew: list = polynomial(xnew)

        fig, ax = plt.subplots()
        ax.grid(True)
        ax.set_title('Thetta to radius')
        plt.plot(xnew, ynew, '-', x, y, '.')

        plt.show()

    def plotZenithDeviation(self, buffer: list | None = None, from_file: str = '') -> None:
        if from_file != '':
            mybuffer: list = self.downloadFile(from_file)
        else:
            mybuffer: list = buffer if buffer.any() else self.imageBuffer
        npbuffer: np.ndarray = np.array(mybuffer)
        angleBuff, deviationBuff = self.defineZenithDeviation(npbuffer)

        fig, ax = plt.subplots()
        ax.grid(True)
        ax.set_title('Zenith angle deviation')
        plt.xlim(-0.5, 60)
        plt.ylim(-0.5, 0.5)
        plt.scatter(angleBuff, deviationBuff, marker='o', c = 'r', label = 'Python data')
        plt.xlabel('Zenith angle')
        plt.ylabel('Zenith angle deviation')
        plt.legend()
        plt.show()
