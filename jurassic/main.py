# importing everything
import pygame
from cubeMap import FlattenCubeMap
from scene import Scene
from lightSource import LightSource
from blender import load_obj_file
from BaseModel import DrawModelFromMesh
from shaders import *
from ShadowMapping import *
from sphereModel import Sphere
from skyBox import *
from environmentMapping import *

class JurassicPark(Scene):
    def __init__(self):
        Scene.__init__(self)

        self.light = LightSource(self, position=[0., 4., -3.])
        self.shaders='phong'

        # for shadow map rendering
        self.shadows = ShadowMap(light=self.light)
        self.show_shadow_map = ShowTexture(self, self.shadows)

        meshes = load_obj_file('models/city.obj')
        self.add_models_list(
            [DrawModelFromMesh(scene=self, M=np.matmul(translationMatrix([0,-3,0]),scaleMatrix([1,1,1])), mesh=mesh, shader=ShadowMappingShader(shadow_map=self.shadows), name='scene') for mesh in meshes]
        )

        # draw a skybox for the horizon
        self.skybox = SkyBox(scene=self)
        self.show_light = DrawModelFromMesh(scene=self, M=poseMatrix(position=self.light.position, scale=0.2), mesh=Sphere(material=Material(Ka=[10,10,10])), shader=FlatShader())
        self.environment = EnvironmentMappingTexture(width=400, height=400)

        dino = load_obj_file('models/dino.obj')
        self.dino1 = DrawModelFromMesh(scene=self, M=np.matmul(np.matmul(rotationMatrixY(np.radians(-90)), translationMatrix([0, -2, 4.5])), scaleMatrix([1, 1, 1])), mesh=dino[0], shader=PhongShader())       
        self.dino2 = DrawModelFromMesh(scene=self, M=np.matmul(translationMatrix([0,-2,0]), scaleMatrix([1,1,1])), mesh=dino[0], shader=PhongShader())
        self.dino3 = DrawModelFromMesh(scene=self, M=np.matmul(translationMatrix([4,-2,0]), scaleMatrix([1,1,1])), mesh=dino[0], shader=EnvironmentShader(map=self.environment))

    def draw_shadow_map(self):
        # first we need to clear the scene, we also clear the depth buffer to handle occlusions
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.dino1.draw()
        self.dino2.draw()
        self.dino3.draw()

    def draw_reflections(self):
        self.skybox.draw()

    def draw(self, framebuffer=False):
        '''
        Draw all models in the scene
        :return: None
        '''
        # first we need to clear the scene, we also clear the depth buffer to handle occlusions
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # when using a framebuffer, we do not update the camera to allow for arbitrary viewpoint.
        if not framebuffer:
            self.camera.update()
        # first, we draw the skybox
        self.skybox.draw()
        # render the shadows
        self.shadows.render(self)

        # when rendering the framebuffer we ignore the reflective object
        if not framebuffer:
            self.environment.update(self)
            self.dino1.draw()
            self.dino2.draw()
            self.dino3.draw()
            self.show_shadow_map.draw()
        # then we loop over all models in the list and draw them
        for model in self.models:
            model.draw()

        self.show_light.draw()

        # once we are done drawing, we display the scene
        # Note that here we use double buffering to avoid artefacts:
        # we draw on a different buffer than the one we display,
        # and flip the two buffers once we are done drawing.
        if not framebuffer:
            pygame.display.flip()

    def keyboard(self, event):
        '''
        Process additional keyboard events for this demo.
        '''
        Scene.keyboard(self, event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                # Perform translation on dino2 in the positive Z direction
                self.dino2.M = np.matmul(self.dino2.M, translationMatrix([0, 0, 0.1]))

            elif event.key == pygame.K_UP:
                # Perform translation on dino2 in the negative Z direction
                self.dino2.M = np.matmul(self.dino2.M, translationMatrix([0, 0, -0.1]))

            elif event.key == pygame.K_LEFT:
                # Perform translation on dino2 in the negative X direction
                self.dino2.M = np.matmul(self.dino2.M, translationMatrix([-0.1, 0, 0]))

            elif event.key == pygame.K_RIGHT:
                # Perform translation on dino2 in the positive X direction
                self.dino2.M = np.matmul(self.dino2.M, translationMatrix([0.1, 0, 0]))

if __name__ == '__main__':
    # initialises the scene object
    scene = JurassicPark()
    # starts drawing the scene
    scene.run()
