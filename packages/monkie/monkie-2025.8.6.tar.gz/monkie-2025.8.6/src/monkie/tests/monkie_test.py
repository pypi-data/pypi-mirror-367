import marimo

__generated_with = "0.14.16"
app = marimo.App(width="medium")

with app.setup:
    # Initialization code that runs before all other cells
    import monkie
    im_path = monkie.__test_path__


@app.cell
def _():
    im, ui = monkie.load(im_path)
    return im, ui


@app.cell
def _(im, ui):
    monkie.show(im, ui)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
