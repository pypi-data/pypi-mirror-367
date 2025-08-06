"""Script for the Failure Analysis on Composite FEM Models."""

# Copyright (c) Idaero Solutions.
# Distributed under the terms of the LICENSE file located in NaxToPy-<version>.dist-info


import NaxToPy as n2p
import numpy as np
from NaxToPy.Core.Classes.N2PProperty import N2PProperty
from NaxToPy.Core.Classes.N2PMaterial import N2PMaterial
from NaxToPy.Core.N2PModelContent import N2PModelContent
from NaxToPy.Core.Classes.N2PLoadCase import N2PLoadCase
from NaxToPy.Core.Classes.N2PComponent import N2PComponent
from NaxToPy.Core.Classes.N2PResult import N2PResult
from NaxToPy.Core.Classes.N2PElement import N2PElement
from NaxToPy.Modules.common.property import *
from NaxToPy.Modules.common.material import *
from NaxToPy.Modules.common.model_processor import *
from NaxToPy.Modules.common.data_input_hdf5 import *
from NaxToPy.Modules.common.hdf5 import *

import time


class N2PCompositeFailure:
    """
    Abstract base class for evaluating structural failure on composites materials
    """

    # __slots__ = ("_model", "_element_list", "_LCs", "_failure_criterion", "_hdf5", "_materials", "_properties", "_properties_elem", "_criteria_dict","mechanical_prop_dict", "Analysis_Results",
                 
    #              )

    def __init__(self):
        """
        Initialize the class

        Args: 
            model: raw data extracted from a N2PModelContent instance user-provided
            elements : list of N2PElements instances where analysis will be performed.
            loadcase : list of N2PLoadCase instances where analysis will be performed.
        """
        # Mandatory attributes [User Input] ------------------------------------------------------------------------------------
        self._model: N2PModelContent = None
        self._element_list: list[N2PElement] = []
        self._LCs: list[N2PLoadCase] = None
        self._failure_criterion: str = None
        self._failure_theory: str = None


        self._hdf5 = HDF5_NaxTo()
        self._materials: dict = None
        self._properties: dict = None
        self._properties_elem: dict = None

        self._criteria_dict = {
            "FirstPly" : " Laminate fails when first ply fails",
            "PlyByPly" : "Laminate fails when every ply fails" 
        }

        self._failureTheory_dict = {
            "TsaiWu" : "Tsai-Wu failure criterion",
            "MaxStress" : "Maximum Stress failure criterion",
            "TsaiHill": "Tsai-Hill failure criterion",
            "Hashin": "Hashin failure criterion",
            "Puck": "Puck failure criterion",
            "FMC" : "Failure Mode Concept (FMC) failure criterion"
        }

        self._initialize_analysis()
        

    def _initialize_analysis(self):
        """
        Method to initialize data transformation from user input to a ModelProcessor instance.

        """
        pass

    
    # Getters ------------------------------------------------------------------------------------------------------------------
    # Method to obtain the model -----------------------------------------------------------------------------------------------
    @property
    def Model(self) -> N2PModelContent:
        """ 
        Property that returns the model attribute, that is, the N2PModelContent object to be analyzed.
        """
        return self._model
    # ----------------------------------------------------------------------------------------------------------------------

    # Method to obtain the List of elements which is going to be analyzed ------------------------------------------------------
    @property
    def Elements(self) -> list[N2PElement]:
        """
        Property that returns the list of elements, that is, the list of elements to be analyzed.
        """
        return self._element_list
    # --------------------------------------------------------------------------------------------------------------------------

    # Method to obtain the List of LoadCases which is going to be analyzed -----------------------------------------------------
    @property
    def LoadCases(self) -> list[N2PLoadCase]:
        """
        Property that returns the list of elements, that is, the list of elements to be analyzed.
        """
        return self._LCs
    # --------------------------------------------------------------------------------------------------------------------------

    # Method to obtain the List of elements which is going to be analyzed ------------------------------------------------------
    @property
    def FailureCriteria(self) -> list[N2PElement]:
        """
        Property that returns the list of elements, that is, the list of elements to be analyzed.
        """
        return self._failure_criterion
    # --------------------------------------------------------------------------------------------------------------------------

        # Method to obtain the List of elements which is going to be analyzed ------------------------------------------------------
    @property
    def FailureTheory(self) -> list[N2PElement]:
        """
        Property that returns the list of elements, that is, the list of elements to be analyzed.
        """
        return self._failure_theory
    # --------------------------------------------------------------------------------------------------------------------------
    
    #Method to obtain the path where results files will be exported ------------------------------------------------------------
    @property
    def HDF5(self) -> HDF5_NaxTo:
        """
        Property that returns the path where ResultsFile will be exported.
        """

        return self._hdf5
    
    #Method to obtain material instances and their elements --------------------------------------------------------------------
    @property
    def Materials(self) -> dict:
        """
        Property that returns a dictionary with Material Instances.
        """
        return self._materials
    
    #Method to obtain property instances and their elements --------------------------------------------------------------------
    @property
    def Properties(self) -> dict:
        """
        Property that returns a dictionary with Property Instances.
        """
        return self._properties

    # Setters ------------------------------------------------------------------------------------------------------------------
    @Model.setter
    def Model(self, value: N2PModelContent) -> None:
        
        if isinstance(value, N2PModelContent):
            self._model = value
            # print("model set successfully.")
        else: 
            msg = N2PLog.Error.E800()
            raise TypeError(msg)
        

    # --------------------------------------------------------------------------------------------------------------------------
    
    
    @Elements.setter
    # @profile
    def Elements(self, value: list[N2PElement]) -> None:

        if all(isinstance(element, N2PElement) for element in value):
            self._element_list = value

            filtered_elements = [element for element in self._element_list if self._model.PropertyDict[element.Prop].PropertyType in ('PCOMP', 'CompositeShellSection')]
            if len(self._element_list) > len(filtered_elements):
                N2PLog.Warning.W800()
            
            self._element_list = filtered_elements

            _, _, self._materials, _ = elem_to_material(self.Model, self._element_list)
            self._properties, self._properties_elem = get_properties(self.Model, self._element_list)

            # print("Elements set successfully.")
        else:
            msg = N2PLog.Error.E801()
            raise TypeError(msg)

    # --------------------------------------------------------------------------------------------------------------------------

    @LoadCases.setter
    def LoadCases(self, value: list[N2PLoadCase]) -> None:
        if all(isinstance(loadcase, N2PLoadCase) for loadcase in value):
            self._LCs = value

            # print("LoadCases set successfully.")

        else:
            msg = N2PLog.Error.E802()
            raise TypeError(msg)
    # --------------------------------------------------------------------------------------------------------------------------

    @FailureCriteria.setter
    def FailureCriteria(self, value: str) -> None:
        if value not in self._criteria_dict:
            msg = N2PLog.Error.E803(value, self._criteria_dict)
            raise TypeError(msg)

        self._failure_criterion = value

    # --------------------------------------------------------------------------------------------------------------------------
    
    @FailureTheory.setter
    def FailureTheory(self, value: str) -> None:
        if value not in self._failureTheory_dict:
            msg = N2PLog.Error.E803(value, self._failureTheory_dict)
            raise TypeError(msg)

        self._failure_theory = value


    # --------------------------------------------------------------------------------------------------------------------------
    
    # @profile
    def forces_tensor(self):
        """
        Extracts forces from the LoadCases and stores them in a tensor.
        
        Returns:
            np.ndarray: A tensor containing forces for each LoadCase, element, and variable.

            The tensor will have the shape (LoadCases, Elements, 6) with the following components:
            - Fx: Force in the x-direction
            - Fy: Force in the y-direction  
            - Fxy: Shear force in the xy-plane
            - Mx: Moment about the x-axis
            - My: Moment about the y-axis
            - Mxy: Moment about the xy-plane
        """
        elements = self.Elements
        n_elements = len(elements)
        load_cases = len(self.LoadCases)
        
        # Extract forces from N2PModelContent
        Forces_element = {LC: self._extract_forces(LC) for LC in self.LoadCases}  

        # Initialize tensors.There will be a tensor for each Force Component. Shape (LoadCases, Elements, Forces). Consider there will be 6 compoinets: Fx, Fy, Fxy, Mx, My, Mxy

        self.Forces_array = np.array([np.nan_to_num(Forces_element[LC][element], nan=0) for LC in self.LoadCases for element in elements])
        self.Forces_array = self.Forces_array.reshape(load_cases, n_elements, 6)  # Reshape to (LoadCases, Elements, 6)

        
        return self.Forces_array  # Shape: (LoadCases, Elements, 6)
    
    # @profile
    def Q_tensor(self):
        """ 
        Computes both Q  matrix and QBar matrix for each lamina in the elements.
        
        """

        #  EXTRACT LAMINATE PROPERTIES. Compute Q matrix and QBar for each Lamina in the CompositeShells.
        
        ## Create a numpy array to store material properties. Shape (n_elements, n_plies, n_variables). Consider the following properties: mat_ID, theta, E1, E2, Nuxy, Nuyx, ShearXY
    

        # Dimensions
        n_loadcases = len(self.LoadCases)
        n_elements = len(self.Elements)
        n_plies = max(len(shell.Laminate) for shell in self.Composite_Shells)
        n_variables = 7  # [mat_ID, theta, E1, E2, Nuxy, Nuyx, ShearXY]
        # n_variables = 9  # [mat_ID, theta, E1, E2, Nuxy, Nuyx, ShearXY, mu21, b2]

        # Initialize Laminate array
        self.laminate_props = np.zeros((n_elements, n_plies, n_variables), dtype= np.float64)  # Use float64 for better precision

        # Fill array for each element and ply
        for i, shell in enumerate(self.Composite_Shells):
            for j, ply in enumerate(shell.Laminate):
                self.laminate_props[i, j, 0] = ply.mat_ID[0]
                self.laminate_props[i, j, 1] = ply.theta
                self.laminate_props[i, j, 2] = ply.Ex
                self.laminate_props[i, j, 3] = ply.Ey
                self.laminate_props[i, j, 4] = ply.Nuxy
                self.laminate_props[i, j, 5] = ply.Nuyx
                self.laminate_props[i, j, 6] = ply.ShearXY
                # self.laminate_props[i, j, 7] = ply.mu21
                # self.laminate_props[i, j, 8] = ply.m 


        # QMATRIX -------------------------------------------------------------------
        """
        Computes the Q matrix for each lamina in the elements based on the laminate properties.
        
        This method calculates the Q matrix, which is a stiffness matrix for composite laminates, using the material properties extracted from the laminate properties array. The Q matrix is essential for further calculations in composite failure analysis.

        It is important to take into consideration the loadcase dimension due to the fact that Qmatrix are material dependant, therefore, aparently similar for every Loadcase. However, this is not completely true. Even if for similar laminates, Qmatrix and QBar are similar, stress distribution is not the same for each loadcase, and plies may not fail at the same time and the ABD Matrix is not the same for each loadcase. Therefore, we need to compute Qmatrix and QBar for each Loadcase.
        
        Returns:
            None: The method initializes the QMatrix_array attribute of the class.
        """

        ## Create a numpy array to store the QMatrix for each lamina in the elements. 3x3 Matrix will be defined by each of its elements. Therefore, shape (n_loadcases, n_elements, n_plies, 9)

        self.QMatrix_array = np.zeros((n_loadcases, n_elements, n_plies, 9), dtype=np.float64)  # Initialize with zeros for better performance
        
        # Compute Q matrix elements, extracting material data from self.laminate_props array.

        # Extract material properties
        E1 = self.laminate_props[:, :, 2]
        E2 = self.laminate_props[:, :, 3]
        Nu12 = self.laminate_props[:, :, 4]
        Nu21 = self.laminate_props[:, :, 5]
        G12 = self.laminate_props[:, :, 6]

        # Compute denominator
        denom = 1 - Nu12 * Nu21

        # Compute Q matrix components
        Q11 = E1 / denom
        Q22 = E2 / denom
        Q12 = Nu12 * E2 / denom
        Q66 = G12

        # Fill QMatrix_array with computed values
        for l in range(n_loadcases):
            for i in range(n_elements):
                for j in range(n_plies):
                    self.QMatrix_array[l, i, j] = [
                        Q11[i, j], Q12[i, j], 0,
                        Q12[i, j], Q22[i, j], 0,
                        0, 0, Q66[i, j]
                    ]   

        # QBAR ----------------------------------------------------------------------
        """
        Computes the QBar matrix for each lamina in the elements based on the laminate properties and rotation matrices.

        This method calculates the QBar matrix, which is a transformed stiffness matrix for composite laminates, using the Q matrix and the rotation matrices derived from the laminate angles. The QBar matrix is essential for further calculations in composite failure analysis.
        
        Returns:
            None: The method initializes the QBar_array and Rotation_array attributes of the class.
        """

        ## Create a numpy array to store the QBar matrix for each lamina in the elements. 3x3 Matrix will be defined by each of its elements. Therefore, shape (n_loadcases, n_elements, n_plies, 9)

        self.QBar_array = np.zeros((n_loadcases, n_elements, n_plies, 9), dtype= np.float64)  # Initialize with zeros for better performance

        # Create a numpy array which contains the rotation matrix for each lamina in the elements. 3x3 Matrix will be defined by each of its elements. Therefore, shape (n_elements, n_plies, 9)

        # Initialize Stress rotation array
        self.Stress_Rotation_array = np.full((n_elements, n_plies, 9), np.nan)
        
        # Pre-compute angles and trig functions
        angles = np.radians(self.laminate_props[:, :, 1])
        c = np.cos(angles)
        s = np.sin(angles)
        
        # Compute STRESS ROTATION MATRIX components using broadcasting
        sigmaR11 = c**2
        sigmaR12 = s**2
        sigmaR13 = 2*c*s
        sigmaR21 = s**2
        sigmaR22 = c**2
        sigmaR23 = -2*c*s
        sigmaR31 = -c*s
        sigmaR32 = c*s
        sigmaR33 = c**2 - s**2
        
        # Fill stress rotation array
        for i in range(n_elements):
                for j in range(n_plies):
                    self.Stress_Rotation_array[i, j] = [
                        sigmaR11[i, j], sigmaR12[i, j], sigmaR13[i, j],
                        sigmaR21[i, j], sigmaR22[i, j], sigmaR23[i, j],
                        sigmaR31[i, j], sigmaR32[i, j], sigmaR33[i, j]
                    ]
                
        # Initialize strain rotation array. As rotation Matrix is orthogonal. You may recall that R-1 = R^T. Therefore, we can compute the inverse rotation matrix by transposing the rotation matrix.

        self.Strain_Rotation_array = np.full((n_elements, n_plies, 9), np.nan)
        
        # Get angles and compute trig functions once
        angles = np.radians(self.laminate_props[:, :, 1])
        c = np.cos(angles)
        s = np.sin(angles)
        
        # Compute STRAIN ROTATION MATRIX components
        strainR_11 = c**2
        strainR_12 = s**2
        strainR_13 = 2*c*s
        strainR_21 = s**2
        strainR_22 = c**2
        strainR_23 = -2*c*s
        strainR_31 = -c*s
        strainR_32 = c*s
        strainR_33 = (c**2 - s**2)

        
        # Fill inverse rotation array
        for i in range(n_elements):
            for j in range(n_plies):
                self.Strain_Rotation_array[i, j] = [
                    strainR_11[i, j], strainR_12[i, j], strainR_13[i, j],
                    strainR_21[i, j], strainR_22[i, j], strainR_23[i, j],
                    strainR_31[i, j], strainR_32[i, j], strainR_33[i, j]
                ]


        # Rebuild the arrays to the correct shape for matrix operations
        strainR = self.Strain_Rotation_array.reshape(n_elements, n_plies, 3, 3)
        Qmatrix = self.QMatrix_array.reshape(n_loadcases, n_elements, n_plies, 3, 3)

        # Invert the strain rotation matrix for each element and ply
        R_inv = self.fast_inverse_3x3(strainR)   

        # Add LoadCase dimension to R_inv
        R_inv = R_inv[np.newaxis, :, :, :, :]  # Shape: (1, n_elements, n_plies, 3, 3)
        R_inv_T = np.transpose(R_inv, axes=(0,1,2,4,3))

        # Compute QBar using einsum
        QBar = np.einsum('lijmp,lijpq,lijqn->lijmn', R_inv, Qmatrix, R_inv_T)

        # Flatten and store
        self.QBar_array = QBar.reshape(n_loadcases, n_elements, n_plies, 9)

        # return self.QMatrix_array, self.QBar_array  # Shape: (n_elements, n_plies, 9) for QMatrix and QBar respectively

        return self.QMatrix_array, self.QBar_array
    
    def fast_inverse_3x3(self, matrix):
        """Fast inverse for batch of 3x3 matrices"""
        # Get matrix elements
        a = matrix[..., 0, 0]
        b = matrix[..., 0, 1]
        c = matrix[..., 0, 2]
        d = matrix[..., 1, 0]
        e = matrix[..., 1, 1]
        f = matrix[..., 1, 2]
        g = matrix[..., 2, 0]
        h = matrix[..., 2, 1]
        i = matrix[..., 2, 2]

        # Calculate determinant
        det = (a * (e * i - f * h) - 
            b * (d * i - f * g) + 
            c * (d * h - e * g))

        # Calculate inverse elements
        inv = np.zeros_like(matrix)
        inv[..., 0, 0] = (e * i - f * h) / det
        inv[..., 0, 1] = (c * h - b * i) / det
        inv[..., 0, 2] = (b * f - c * e) / det
        inv[..., 1, 0] = (f * g - d * i) / det
        inv[..., 1, 1] = (a * i - c * g) / det
        inv[..., 1, 2] = (c * d - a * f) / det
        inv[..., 2, 0] = (d * h - e * g) / det
        inv[..., 2, 1] = (b * g - a * h) / det
        inv[..., 2, 2] = (a * e - b * d) / det

        return inv 
    
    # @profile
    def ABD_tensor(self, QBar):

        # ABD Matrix -----------------------------------------------------------------
        """
        Computes the ABD matrix for each element based on the laminate properties.

        This method calculates the ABD matrix for each element and load case using the laminate properties, QBar matrices, and thicknesses of the laminas. The ABD matrix is a 6x6 matrix that relates the forces and moments to the strains and curvatures in composite laminates.


        Returns:
            np.ndarray: A tensor containing the ABD matrix for each element and load case.
        """

        # Dimensions
        # n_loadcases = len(self.LoadCases)
        # n_elements = len(self.Elements)
        # n_plies = max(len(shell.Laminate) for shell in self.Composite_Shells)

        # create a numpy array to store the thicknesses of each ply on each element. Shape (n_elements, n_plies)

        # thicknesses = np.full((n_elements, n_plies), np.nan)

        # for i, shell in enumerate(self.Composite_Shells):
        #     for j, ply in enumerate(shell.Laminate):
        #         thicknesses[i, j] = ply.thickness


        # total_thickness = np.full((n_elements, 1), np.nan)  # Variable length
        # for i, shell in enumerate(self.Composite_Shells):
        #     total_thickness[i] = np.sum(shell._thicknesses)

        # create a numpy array to store the lower reference of the laminate for each element. Shape (n_elements). We consider lower reference as half the thickness of the laminate. Therefore, we can compute it by summing the thicknesses of all plies and dividing by 2.

        # lower_ref = np.full((n_elements, 1), np.nan) # Variable length
        # for i, shell in enumerate(self.Composite_Shells):
        #     lower_ref[i] = -np.sum(shell._thicknesses) / 2  # Variable length

        # create a numpy array to store the centroid of each lamina on each element with regard to lower reference. Shape (n_elements, n_plies)
        # Initialize centroid array
        # self.centroid = np.full((n_elements, n_plies), np.nan)

        # Calculate cumulative thicknesses
        # cumulative_thickness = np.cumsum(thicknesses, axis=1)

        # Lower reference + cumulative thickness - half thickness of current ply
        # for i in range(n_elements):
        #     for j in range(n_plies):
        #         if j == 0:
        #             self.centroid[i, j] = lower_ref[i] + (cumulative_thickness[i, j] - (thicknesses[i, j] / 2))
        #         else:
        #             self.centroid[i, j] = lower_ref[i] + cumulative_thickness[i, j] - (thicknesses[i, j] / 2)


        # Initialize A Matrix array
        # self.AMatrix_array = np.full((n_loadcases,n_elements, 9), np.nan)
        # Initialize B Matrix array
        # self.BMatrix_array = np.full((n_loadcases, n_elements, 9), np.nan)
        # Initialize D Matrix array
        # self.DMatrix_array = np.full((n_loadcases, n_elements, 9), np.nan)
        # Initialize ABD Matrix array
        # self.ABDMatrix_array = np.full((n_loadcases, n_elements, 36), np.nan)
        # Compute A, B, D matrices
        # for l in range(n_loadcases):
        #     for i in range(n_elements):
        #         A = np.zeros((3, 3))
        #         B = np.zeros((3, 3))
        #         D = np.zeros((3, 3))

        #         for j in range(n_plies):
        #             QBar = self.QBar_array[l, i, j].reshape(3, 3)
        #             t = thicknesses[i, j]

        #             Compute A, B, D contributions
        #             A += QBar * t
        #             B += QBar * t * self.centroid[i, j]
        #             D += QBar * t * (self.centroid[i, j] ** 2)

        #         Store matrices in the respective arrays
        #         self.AMatrix_array[l, i] = A.flatten()
        #         self.BMatrix_array[l, i] = B.flatten()
        #         self.DMatrix_array[l, i] = D.flatten()

        #         Combine into ABD matrix
        #         self.ABDMatrix_array[l, i] = np.block([[A, B], [B.T, D]]).flatten()

        # Get dimensions
        n_loadcases = len(self.LoadCases)
        n_elements = len(self.Elements)
        n_plies = max(len(shell.Laminate) for shell in self.Composite_Shells)

        
        
        # Initialize arrays with LoadCase dimension
        self.AMatrix_array = np.zeros((n_loadcases, n_elements, 9), dtype= np.float64)
        self.BMatrix_array = np.zeros((n_loadcases, n_elements, 9), dtype= np.float64)
        self.DMatrix_array = np.zeros((n_loadcases, n_elements, 9), dtype= np.float64)
        self.ABDMatrix_array = np.zeros((n_loadcases, n_elements, 36), dtype= np.float64)  # Use float64 for better precision


        # Reshape QBar for matrix operations (L, n_elements, n_plies, 3, 3)
        QBar = QBar.reshape(n_loadcases, n_elements, n_plies, 3, 3)
        
        # Compute A, B, D matrices using broadcasting
        t = self.thicknesses[None, :, :, None, None]  # Shape: (1, n_elements, n_plies, 1, 1)
        z = self.centroid[None, :, :, None, None]  # Shape: (1, n_elements, n_plies, 1, 1)
        
        # Calculate matrices for all load cases at once
        A = np.sum(QBar * t, axis=2)  # Sum over plies
        B = np.sum(QBar * t * z, axis=2)
        D = np.sum(QBar * (t * (z**2) + (t**3)/12), axis=2)

        # Store results
        self.AMatrix_array = A.reshape(n_loadcases, n_elements, 9)
        self.BMatrix_array = B.reshape(n_loadcases, n_elements, 9)
        self.DMatrix_array = D.reshape(n_loadcases, n_elements, 9)

        # Create ABD matrices
        A = A.reshape(n_loadcases, n_elements, 3, 3)
        B = B.reshape(n_loadcases, n_elements, 3, 3)
        D = D.reshape(n_loadcases, n_elements, 3, 3)
        
        # Combine into ABD matrix using block structure
        self.ABDMatrix_array = np.block([
            [A, B],
            [B, D]
        ]).reshape(n_loadcases, n_elements, 36)

        return self.ABDMatrix_array

    

    # @profile
    def forces_stresses(self, Forces, ABDMatrix, QMatrix):

        # COMPUTE STRAINS FROM FORCES -------------------------------------------------------------
        """
        Computes the strains from the forces applied to the elements based on the Fundamental equation of Classical Laminate Theory.

        This method calculates the strains for each element and load case using the ABD matrix and the forces applied to the elements. The strains are computed using the fundamental equation of classical laminate theory, which relates forces and moments to strains and curvatures in composite laminates.

        Returns:
            np.ndarray: A tensor containing the stresses for each load case, element, and ply.

        """

        # Dimensions
        n_loadcases = len(self.LoadCases)
        n_elements = len(self.Elements)
        n_plies = max(len(shell.Laminate) for shell in self.Composite_Shells)

        # Initialize the StrainBar array
        self.StrainBar_array = np.full((n_loadcases, n_elements, n_plies, 3), np.nan)

        # # Adjust the ABD Array to match the requested shape for the Strain calculation. [ABD]^-1 @ Forces_array
        # ABD_inv = np.linalg.inv(ABDMatrix.reshape(n_loadcases, n_elements, 6, 6))  # Inverse of ABD matrix

        # Reshape ABDMatrix
        ABD_reshaped = ABDMatrix.reshape(n_loadcases, n_elements, 6, 6)

        # Create mask for non-zero matrices
        non_zero_mask = ~np.all(np.abs(ABD_reshaped) < 1e-10, axis=(2,3))

        # Initialize inverse array with zeros
        ABD_inv = np.zeros_like(ABD_reshaped)

        # Get indices of non-zero matrices
        non_zero_indices = np.where(non_zero_mask)

        # Compute inverses for non-zero matrices in single operation
        ABD_inv[non_zero_indices] = np.linalg.inv(ABD_reshaped[non_zero_indices])

        # Calculate mid-plane strains and curvatures using proper einsum notation
        strains_curvature = np.einsum('abij,abi->abj', ABD_inv, Forces)
        
        # Split into midplane strains and curvatures
        epsilon_0 = strains_curvature[:, :, :3]  # (loadcases, elements, 3)
        kappa = strains_curvature[:, :, 3:]      # (loadcases, elements, 3)
        
        # Compute strains using broadcasting
        z = self.centroid  

        # Reshape z for broadcasting
        z = z[:, :, np.newaxis]  # Shape: (n_elements, n_plies, 1)
        
        # Add ply dimension to epsilon_0 and kappa
        epsilon_0 = epsilon_0[..., np.newaxis, :]  # Shape: (n_loadcases, n_elements, 1, 3)
        kappa = kappa[..., np.newaxis, :]         # Shape: (n_loadcases, n_elements, 1, 3)
        
        # Calculate all strains at once using broadcasting
        self.StrainBar_array[..., :3] = epsilon_0 + kappa * z[None, :, :, :]

        # Rotate strains to material coordinates
        # Initialize the StrainMat_array
        self.StrainMat_array = np.full((len(self.LoadCases), n_elements, n_plies, 3), np.nan)
                    
        # Reshape rotation matrices to (elements, plies, 3, 3)
        strainR = self.Strain_Rotation_array.reshape(n_elements, n_plies, 3, 3)
        
        # Add loadcase dimension to rotation matrices (1, elements, plies, 3, 3)
        strainR = strainR[np.newaxis, ...] # shape (1, n_elements, n_plies, 3, 3)

        # Reshape arrays for batch multiplication
        strains_glo = self.StrainBar_array[..., :3, np.newaxis] # shape (LoadCases, Elements, Plys, 3, 1)

        # Compute rotated strains using einsum
        strains_loc = np.einsum('lijmn, lijno ->lijmo', strainR, strains_glo)

        # Store results
        self.StrainMat_array[..., :3] = strains_loc.squeeze(-1)



        # COMPUTE STRESSES FROM STRAINS -------------------------------------------------------------
        """
        Computes the stresses from the strains calculated for each element and load case.
        This method calculates the local stresses for each ply for each element and load case using the constitutive equations of composite materials. 
         
        It uses QMatrix matrices and the strains computed in the previous step. The stresses are computed using the formula σ = QMatrix * ε, where σ is the stress vector and ε is the strain vector.

        Returns:
            np.ndarray: A tensor containing the local stresses for each load case, element, and ply.
        
        """

        # Initialize Stress array
        self.StressMat_array = np.full((n_loadcases, n_elements, n_plies, 3), np.nan)

        # # Reshape QMatrix for batch operations (elements, plies, 3, 3)
        # Q = QMatrix.reshape(n_loadcases, n_elements, n_plies, 3, 3)


        # # Reshape strains for batch multiplication
        # strains = self.StrainMat_array[..., :3, np.newaxis]  # Shape: (LC, E, P, 3, 1)

        # # Compute all stresses at once using einsum
        # stresses = np.einsum('lijmn, lijno ->lijmo', Q, strains)

        # # Store results
        # self.StressMat_array[..., :3] = stresses.squeeze(-1)

        # Replace Q = QMatrix.reshape(...) with:
        Q = self.QBar_array.reshape(n_loadcases, n_elements, n_plies, 3, 3)

        # Apply QBar to strain_global (no pre-rotation)
        stresses_global = np.einsum('lijmn, lijno -> lijmo', Q, strains_glo)

        # Then rotate stress using Stress_Rotation_array
        R = self.Stress_Rotation_array.reshape(n_elements, n_plies, 3, 3)[np.newaxis, ...]
        stresses_material = np.einsum('lijmn, lijno -> lijmo', R, stresses_global)

        self.StressMat_array = stresses_material.squeeze(-1)


        return self.StressMat_array  # Shape: (LoadCases, Elements, Plys, 3)
    
    # @profile
    def allowables_tensor(self):
        """
        Computes the allowables tensor for each element based on the material properties.

        This method extracts the allowables for each material used in the elements and organizes them into a tensor. The tensor will have the shape (n_elements, n_plies, 5), where 5 corresponds to the following allowables:
            - XTensile
            - XCompressive
            - YTensile
            - YCompressive
            - Shear
        
        Returns:
            np.ndarray: A tensor containing the allowables for each element and ply.
        
        """

        elements = list(self._properties_elem.keys())
        n_elements = len(elements)
        max_laminate = max(len(prop.Laminate) for prop in self._properties.values())
        n_variables = 5
    
        # Initialize tensor with NaN
        self.Allowables_tensor = np.full((n_elements, max_laminate, n_variables), np.nan)
    
        # Precompute allowables for each material
        material_allowables = {
            mat_id: [
                mat.Allowables.XTensile,
                mat.Allowables.XCompressive,
                mat.Allowables.YTensile,
                mat.Allowables.YCompressive,
                mat.Allowables.Shear
            ]
            for mat_id, mat in self.Materials.items()
        }
    
        # Fill the tensor
        for i, element in enumerate(elements):
            prop = self._properties_elem[element]
            for j, lamina in enumerate(prop.Laminate):
                self.Allowables_tensor[i, j, :] = material_allowables[lamina.mat_ID]
    
        return self.Allowables_tensor  # Shape: (n_elements, n_plies, 5)
    
    def coeffs_FMC(self):
        """
        Extracts the coefficients for the FMC failure criterion from the Materials attribute.
        """
        elements = list(self._properties_elem.keys())
        n_elements = len(elements)
        max_laminate = max(len(prop.Laminate) for prop in self._properties.values())

        n_variables = 2 # mu21, m

        # Initialize tensor with NaN
        self.FMC_tensor = np.full((n_elements, max_laminate, n_variables), np.nan)

        # Extract coefficients for each material.
        FMC_material_coeffs = {
            mat_id: [
                mat.mu21,
                mat.m
            ]
            for mat_id, mat in self.Materials.items()
        }

        # Fill the tensor
        for i, element in enumerate(elements):
            prop = self._properties_elem[element]
            for j, lamina in enumerate(prop.Laminate):
                self.FMC_tensor[i, j, :] = FMC_material_coeffs[lamina.mat_ID]
    
        return self.FMC_tensor  # Shape: (n_elements, n_plies, 2)


# -------------------------------------------- CRITERION DEFINITION -----------------------------------------------------------
   
# TSAI-WU----------------------------------------------------------------------------------------------------------------------
     
    # @profile
    def coeffs_TsaiWu(self, Allowables):
        """
        Computes the Tsai-Wu coefficients tensor based on the material allowables.

        This method calculates the Tsai-Wu coefficients for each element and ply based on the material allowables. The coefficients are derived from the allowables and are used in the Tsai-Wu failure criterion.

        Returns:
            np.ndarray: A tensor containing the Tsai-Wu coefficients for each element and ply. Shape: (n_elements, n_plies, 6)

        """

        Xt = Allowables[:, :, 0]  # Shape: (n_elements, n_plies)
        Xc = Allowables[:, :, 1]
        Yt = Allowables[:, :, 2]
        Yc = Allowables[:, :, 3]
        S = Allowables[:, :, 4]

        # Prevent divide by zero warnings (replace 0s with np.nan or a small number)
        Xt[Xt == 0] = np.nan
        Xc[Xc == 0] = np.nan
        Yt[Yt == 0] = np.nan
        Yc[Yc == 0] = np.nan
        S[S == 0] = np.nan

        F1 = 1 / Xt - 1 / Xc
        F2 = 1 / Yt - 1 / Yc
        F11 = 1 / (Xt * Xc)
        F22 = 1 / (Yt * Yc)
        F66 = 1 / (S ** 2)
        F12 = -0.5 * np.sqrt(F11 * F22)

        # Stack along axis 2 (laminas)
        self.TsaiWu_tensor = np.stack([F1, F2, F11, F22, F66, F12], axis=2)

        return self.TsaiWu_tensor  # Shape: (n_elements, n_plies, 6)
        
    # @profile
    def compute_TsaiWu(self, Stresses, TsaiWu_tensor):
        """
        Computes the Tsai-Wu failure criterion for composite materials.
        This method calculates the Reserve Factor (RF) tensor based on the Tsai-Wu 
        failure criterion using stress tensors and material allowables. The RF is 
        computed as the solution to a quadratic equation derived from the Tsai-Wu 
        failure theory.
        Returns:
            np.ndarray: A tensor containing the Reserve Factor (RF) values for 
            each load case, element, and ply. Shape: (Load Cases, Elements, Plies).
        Notes:
            - The method assumes that the stress tensor, allowables tensor, and 
              Tsai-Wu coefficients tensor are precomputed and available.
            - Negative discriminants in the quadratic formula are clipped to zero 
              to avoid complex roots.
            - Division by zero in the quadratic formula is handled by assigning 
              NaN to the corresponding RF values.
        """

        
        # Unpack stresses
        sigma1 = Stresses[..., 0]
        sigma2 = Stresses[..., 1]
        tau12  = Stresses[..., 2]

        # Unpack Tsai-Wu coefficients
        F1  = TsaiWu_tensor[:, :, 0]   # shape (n_elements, n_plies)
        F2  = TsaiWu_tensor[:, :, 1]
        F11 = TsaiWu_tensor[:, :, 2]
        F22 = TsaiWu_tensor[:, :, 3]
        F66 = TsaiWu_tensor[:, :, 4]
        F12 = TsaiWu_tensor[:, :, 5]

        # Expand to (1, Elem, Ply) to match (LC, Elem, Ply)
        def expand(arr): return arr[np.newaxis, :, :]  # (1, Elem, Ply)
        F1, F2, F11, F22, F66, F12 = map(expand, [F1, F2, F11, F22, F66, F12])

        # Transpose stress_tensor from (LC, Ply, Elem, Var) -> (LC, Ply, Elem)
        σ1 = sigma1
        σ2 = sigma2
        τ12 = tau12

        # Compute quadratic form a, b, c
        a = F11 * σ1**2 + F22 * σ2**2 + F66 * τ12**2 + 2 * F12 * σ1 * σ2
        b = F1 * σ1 + F2 * σ2  # ignoring F6 * τ12
        c = -1

        # Replace np.nan with 0 to avoid NaN in calculations
        a = np.nan_to_num(a, nan=0.0)
        b = np.nan_to_num(b, nan=0.0)
        c = np.nan_to_num(c, nan=0.0)

        # Solve Tsai-Wu RF as quadratic formula: RF = (-b + sqrt(b² - 4ac)) / (2a)
        discriminant = b**2 - 4 * a * c
        discriminant = np.where(discriminant < 0, 0, discriminant)  # clip negative roots

        # RF = (-b + np.sqrt(discriminant)) / (2 * a)
        # RF = np.where(a == 0, np.inf, (-b + np.sqrt(discriminant)) / (2 * a))  # avoid div by zero

        with np.errstate(divide='ignore', invalid='ignore'):
            denominator = 2 * a
            RF = np.where(
                (np.abs(denominator) < 1e-10) | (a == 0),
                np.inf,
                (-b + np.sqrt(discriminant)) / denominator
            )

        self.RF_TsaiWu_tensor = RF

        return self.RF_TsaiWu_tensor

# -----------------------------------------------------------------------------------------------------------------------------    

# MAXIMUM STRESS --------------------------------------------------------------------------------------------------------------

    def compute_MaxStress(self, Stresses, Allowables):
        """
        Computes the Maximum Stress failure criterion for composite materials.
        
        This method calculates the Reserve Factor (RF) tensor based on the Maximum Stress
        failure criterion using stress tensors and material allowables. The RF is computed
        as the minimum of the ratios of the allowables to the stresses for each load case,
        element, and ply.

        Returns:
            np.ndarray: A tensor containing the Reserve Factor (RF) values for each load case,
            element, and ply. Shape: (Load Cases, Elements, Plys).

        """

        # Unpack stresses
        sigma1 = Stresses[..., 0]
        sigma2 = Stresses[..., 1]
        tau12  = Stresses[..., 2]

        # Unpack allowables
        Xt = Allowables[..., 0]  # Shape: (n_elements, n_plies)
        Xc = Allowables[..., 1]
        Yt = Allowables[..., 2]
        Yc = Allowables[..., 3]
        S = Allowables[..., 4]

        # Expand to (1, Elem, Ply) to match (LC, Elem, Ply)
        def expand(arr): return arr[np.newaxis, :, :]  # (1, Elem, Ply)
        Xt, Xc, Yt, Yc, S = map(expand, [Xt, Xc, Yt, Yc, S])

        # Reserve Factor Computation

        # RFs_sigma1 = np.where(sigma1 == 0, 0.0, (np.where(sigma1 > 0, Xt/ sigma1, Xc / abs(sigma1))) )  # RF for σ1
        # RFs_sigma2 = np.where(sigma2 == 0, 0.0, (np.where(sigma2 > 0, Yt / sigma2, Yc / abs(sigma2))))  # RF for σ2
        # RFs_tau12 = np.where(tau12 == 0, 0.0, S / abs(tau12))  # RF for τ12

        with np.errstate(divide='ignore', invalid='ignore'):
            # Threshold for "zero" values
            eps = 1e-10
            
            # RF for σ1
            RFs_sigma1 = np.where(
                abs(sigma1) < eps,
                np.inf,
                np.where(sigma1 > 0, Xt/sigma1, Xc/abs(sigma1))
            )
            
            # RF for σ2
            RFs_sigma2 = np.where(
                abs(sigma2) < eps,
                np.inf,
                np.where(sigma2 > 0, Yt/sigma2, Yc/abs(sigma2))
            )
            
            # RF for τ12
            RFs_tau12 = np.where(
                abs(tau12) < eps,
                np.inf,
                S/abs(tau12)
            )

        
        # Compute the Reserve Factor (RF) as the minimum of the RFs
        RFs = np.minimum(RFs_sigma1, RFs_sigma2)  # Minimum of σ1 and σ2 RFs
        RFs = np.minimum(RFs, RFs_tau12)  # Minimum of τ12 RFs
        RFs = np.where(RFs == 0, np.inf, RFs)  # Replace NaN with inf to avoid division by zero
        
        self.RF_MaxStress_tensor = RFs  # Store the RF tensor
        
        return self.RF_MaxStress_tensor  # Shape: (Load Cases, Elements, Plys)

# -----------------------------------------------------------------------------------------------------------------------------   

# TSAI-HILL -------------------------------------------------------------------------------------------------------------------
    def compute_TsaiHill(self, Stresses, Allowables):
        """
        Computes the Tsai-Hill failure criterion for composite materials.
        
        This method calculates the Reserve Factor (RF) tensor based on the Tsai-Hill
        failure theory using stress tensors and material allowables. The RF is computed
        as the solution to a quadratic equation derived from the Tsai-Hill failure theory.

        Returns:
            np.ndarray: A tensor containing the Reserve Factor (RF) values for each load case,
            element, and ply. Shape: (Load Cases, Elements, Plys).
        """
        
        # Unpack stresses
        sigma1 = Stresses[..., 0]
        sigma2 = Stresses[..., 1]
        tau12  = Stresses[..., 2]

        # Unpack allowables
        Xt = Allowables[..., 0]
        Xc = Allowables[..., 1]
        Yt = Allowables[..., 2]
        Yc = Allowables[..., 3]
        S = Allowables[..., 4]
        
        # Expand to (1, Elem, Ply) to match (LC, Elem, Ply)
        def expand(arr): return arr[np.newaxis, :, :]  # (1, Elem, Ply)
        Xt, Xc, Yt, Yc, S = map(expand, [Xt, Xc, Yt, Yc, S])


        # F11 = np.where(sigma1 == 0, 0.0, (np.where(sigma1 > 0, (1 / Xt)**2,  (1 / Xc)**2)))
        # # F12 = np.where(sigma1 == 0, 0.0, (np.where(sigma1 > 0, (-1 / 2*(Xt**2)), (-1 / 2*(Xc**2)))))
        # F12 = np.where(sigma1*sigma2 == 0, 0.0, (1 / Xt * Yt))
        # F22 = np.where(sigma2 == 0, 0.0, (np.where(sigma2 > 0, (1 / Yt)**2,  (1 / Yc)**2)))
        # F66 = np.where(tau12 == 0, 0.0, (1 / S)**2)

        # Q = F11 * sigma1**2
        # # Q += 2 * F12 * sigma1 * sigma2
        # Q += F12 * sigma1 * sigma2
        # Q += F22 * sigma2**2
        # Q += F66 * tau12**2

        # # Replace np.nan with 0 to avoid NaN in calculations
        # Q = np.nan_to_num(Q, nan=0.0)
        # # RF = 1 / (abs(Q)**0.5)
        # RF = np.where(Q == 0, np.inf, 1 / np.sqrt(np.abs(Q)))  # Avoid division by zero

        # Reserve Factor Computation
        term1 = np.where(sigma1 == 0, 0.0, (np.where(sigma1 > 0, (sigma1 / Xt)**2, (sigma1 / Xc)**2)))  # RF for σ1
        term2 = np.where(sigma2 == 0, 0.0, (np.where(sigma2 > 0, (sigma2 / Yt)**2, (sigma2 / Yc)**2)))  # RF for σ2
        term3 = np.where(tau12 == 0, 0.0, (tau12 / S)**2)  # RF for τ12
        term4 = np.where(np.logical_or(sigma1 == 0, sigma2 == 0), 0.0, np.where(sigma1>0, (sigma1 * sigma2)/(Xt * Xt),(sigma1 * sigma2)/(Xc * Xc) ))  # RF for σ1σ2

        a = term1 + term2 + term3 - term4  # Coefficient for the quadratic equation

        # Replace np.nan with 0 to avoid NaN in calculations
        with np.errstate(divide='ignore', invalid='ignore'):
                    denominator = np.sqrt(np.abs(a))
                    RF = np.where(
                        (np.abs(denominator) < 1e-10) | (a == 0),
                        np.inf,
                        1 / denominator
                    )




        # a = np.nan_to_num(a, nan=0.0)
        # RF = np.where(a == 0, np.inf, 1 / (abs(a)**0.5))  # Avoid division by zero
        # # RF = 1 / (abs(a)**0.5)
        # # RF = np.where(a == 0, np.inf, RF)  # Avoid division by zero

        self.RF_TsaiHill_tensor = RF  # Store the RF tensor

        return self.RF_TsaiHill_tensor  # Shape: (Load Cases, Elements, Plys)

# -----------------------------------------------------------------------------------------------------------------------------

# HASHIN ----------------------------------------------------------------------------------------------------------------------

    def compute_Hashin(self, Stresses, Allowables):
        """
        Computes the Hashin failure criterion for composite materials.
        
        This method calculates the Reserve Factor (RF) tensor based on the Hashin failure
        theory using stress tensors and material allowables.
         
        This method evaluates failure modes (fiber and matrix failure) for 
        composite laminates under combined loading conditions.

        Returns:
            np.ndarray: A tensor containing the Reserve Factor (RF_fiber, RF_matrix) values for each load case,
            element, and ply. Shape: (Load Cases, Elements, Plys, 2).
        """
        
        # Unpack stresses
        sigma1 = Stresses[..., 0]
        sigma2 = Stresses[..., 1]
        tau12  = Stresses[..., 2]

        # Unpack allowables
        Xt = Allowables[..., 0]
        Xc = Allowables[..., 1]
        Yt = Allowables[..., 2]
        Yc = Allowables[..., 3]
        S = Allowables[..., 4]

        # Expand to (1, Elem, Ply) to match (LC, Elem, Ply)
        def expand(arr): return arr[np.newaxis, :, :]  # (1, Elem, Ply)
        Xt, Xc, Yt, Yc, S = map(expand, [Xt, Xc, Yt, Yc, S])

        # Reserve Factor Computation
        
        # Fiber failure modes
        RF_fiber = np.where(
            sigma1 == 0,
            0.0,
            np.where(
                sigma1 > 0,
                (1/((sigma1 / Xt) ** 2 + (tau12 / S) ** 2))**0.5, # Fiber tensile failure
                (1/((sigma1 / Xc) ** 2))**0.5 # Fiber compressive failure
            )                
        )
        
        L = (0.25*(Yc/S**2)-(1/Yc))*sigma2
        Q = (0.25*(sigma2**2)/(S**2)) + ((tau12**2)/(S**2))
        
        # Matrix failure modes
        RF_matrix = np.where(
            sigma2 == 0,
            0.0,
            np.where(
                sigma2 > 0,
                ( 1 /((sigma2 / Yt) ** 2 + (tau12 / S) ** 2)) ** 0.5, # Matrix tensile failure
                (-L + (L**2 + 4*Q)**0.5)/(2*Q) # Matrix compressive failure
            )
        )  

        # Initialize array with correct shape
        RF = np.zeros((*RF_fiber.shape, 2))  # Shape: (L, e, ply, 2)
        
        # Fill fiber and matrix RFs
        RF[..., 0] = RF_fiber  # First index for fiber
        RF[..., 1] = RF_matrix  # Second index for matrix
        
        # Replace 0 with np.inf for future calculations
        RF[..., 0] = np.where(RF[..., 0] == 0.0, np.inf, RF[..., 0])  # Fiber RF
        RF[..., 1] = np.where(RF[..., 1] == 0.0, np.inf, RF[..., 1])  # Matrix RF
        self.RF_Hashin_Tensor = RF  # Store the RF tensor
        
        return self.RF_Hashin_Tensor  # Shape: (Load Cases, Elements, Plys, 2)

# -----------------------------------------------------------------------------------------------------------------------------

# PUCK ------------------------------------------------------------------------------------------------------------------------

    def compute_Puck(self, Stresses, Allowables):
        """
        Method to implement the Puck Failure Criterion.

        This method evaluates failure modes (fiber failure and matrix failure) for 
        composite laminates under combined loading conditions.
        
        Returns:
            np.ndarray: A tensor containing the Reserve Factor (RF_fiber, RF_matrix) values for each load case,
            element, and ply. Shape: (Load Cases, Elements, Plys, 2).

        ** In Puck’s theory, the failure plane is not necessarily aligned with the material axes. Instead, it is inclined by an angle 𝜃(typically from −90∘ to +90∘), and failure is evaluated on this plane.

        Puck defines 𝑓𝐼(𝜃)=tan(𝜃)

        So the more inclined the fracture plane is, the larger the shear contribution to matrix failure.

        But that’s only part of the full Puck approach. The inclination angle also affects normal and shear stresses on the fracture plane, which are used to build the full failure criterion. **
        """

        # According to Puck and Schürmann. A default engineering value can be used when fracture plane is unknown.

        fi = 1.12

        # Unpack stresses
        sigma1 = Stresses[..., 0]  # Normal stress in fiber direction
        sigma2 = Stresses[..., 1]  # Normal stress in transverse direction
        tau12  = Stresses[..., 2]  # Shear stress in the plane of the laminate
        
        # Unpack allowables
        Xt = Allowables[..., 0]  # Tensile strength in fiber direction
        Xc = Allowables[..., 1]  # Compressive strength in fiber direction
        Yt = Allowables[..., 2]  # Tensile strength in transverse direction
        Yc = Allowables[..., 3]  # Compressive strength in transverse direction
        S = Allowables[..., 4]   # Shear strength in the plane of the laminate
        
        # Expand to (1, Elem, Ply) to match (LC, Elem, Ply)
        def expand(arr): return arr[np.newaxis, :, :]  # (1, Elem, Ply)
        Xt, Xc, Yt, Yc, S = map(expand, [Xt, Xc, Yt, Yc, S])
        
        # Reserve Factor Computation
        
        # Fiber failure modes
        RF_fiber = np.where(
            sigma1 == 0,
            0.0,
            np.where(
                sigma1 > 0,
                Xt / sigma1,  # Fiber tensile failure
                Xc / abs(sigma1)  # Fiber compressive failure
            )
        )
        
        # Matrix failure modes
        L = ((sigma2/Yc) + fi * abs(tau12)/S)**2
        Q = ((sigma2/Yc) + fi * abs(tau12)/S)**2
        RF_matrix = np.where(
            sigma2 == 0,
            0.0,
            np.where(
                sigma2 > 0,
                1 / ((sigma2/Yt)**2 + (tau12/S)**2)**0.5,  # Matrix tensile failure
                1 / (Q + L)**0.5  # Matrix compressive failure
            )
        )
        
        # Initialize array with correct shape
        RF = np.zeros((*RF_fiber.shape, 2))  # Shape: (L, e, ply, 2)
        # Fill fiber and matrix RFs
        RF[..., 0] = RF_fiber  # First index for fiber
        RF[..., 1] = RF_matrix  # Second index for matrix
        # Replace 0 with np.inf for future calculations
        RF[..., 0] = np.where(RF[..., 0] == 0.0, np.inf, RF[..., 0])  # Fiber RF
        RF[..., 1] = np.where(RF[..., 1] == 0.0, np.inf, RF[..., 1])  # Matrix RF
        
        self.RF_Puck_Tensor = RF  # Store the RF tensor
        
        return self.RF_Puck_Tensor  # Shape: (Load Cases, Elements, Plys, 2)

# -----------------------------------------------------------------------------------------------------------------------------

# FMC ----------------------------------------------------------------------------------------------------------------------
    def compute_FMC(self, Stresses, Allowables, FMC_coeffs):
        """
        Computes the FMC (Fiber Mode Concept) failure criterion for composite materials.

        This method evaluates FF (fiber failure) and IFF (interlaminar fiber failure) failure modes for composite laminates under combined loading conditions.

        Returns:
            np.ndarray: A tensor containing the Reserve Factor (RF) values for each load case,
            element, and ply. Shape: (Load Cases, Elements, Plys, 1).
        
        """

        # Unpack Stresses
        sigma1 = Stresses[..., 0]
        sigma2 = Stresses[..., 1]
        sigma12 = Stresses[..., 2]

        # Unpack allowables and FMC required properties
        mu21 = FMC_coeffs[..., 0] # friction coefficient between plies 
        m = FMC_coeffs[..., 1]  # exponent for the FMC criterion, typically m = 2.0
        Xt = Allowables[..., 0]  # Tensile strength in fiber direction
        Xc = Allowables[..., 1]  # Compressive strength in fiber direction
        Yt = Allowables[..., 2]  # Tensile strength in transverse direction
        Yc = Allowables[..., 3]  # Compressive strength in transverse direction
        S = Allowables[..., 4]   # Shear strength in the plane of the laminate

        # Compute failure modes

        m = np.nan_to_num(m, nan=1.0)

        # FF_1 = np.where(
        #     sigma1 > 0,
        #     (sigma1 / Xt) ** m, 
        #     (np.abs(sigma1) / Xc) ** m
        # )

        with np.errstate(divide='ignore', invalid='ignore'):
            # Safe division and power operations
            FF_1 = np.where(
                ~np.isfinite(sigma1) | (sigma1 == 0),
                np.nan,
                np.where(
                    sigma1 > 0,
                    (sigma1 / Xt) ** m,
                    (np.abs(sigma1) / Xc) ** m
                )
            )

        FF_1 = np.nan_to_num(FF_1, nan=0.0)

        # IFF_1 = np.where(
        #     sigma2 > 0,
        #     (sigma2 / Yt) ** m,
        #     (np.abs(sigma2) / Yc) ** m

        # )

        with np.errstate(divide='ignore', invalid='ignore'):
            # Safe division and power operations
            IFF_1 = np.where(
                ~np.isfinite(sigma2) | (sigma2 == 0),
                np.nan,
                np.where(
                    sigma2 > 0,
                    (sigma2 / Yt) ** m,
                    (np.abs(sigma2) / Yc) ** m
                )
            )

        IFF_1 = np.nan_to_num(IFF_1, nan=0.0)

        IFF_2 = np.where(
            np.abs(sigma12 + mu21[None, :, :]*sigma2) > 0,
            (np.abs(sigma12 + mu21[None, : :]*sigma2) / S) ** m,
            0
        )

        # with np.errstate(divide='ignore', invalid='ignore'):
        #     numerator = np.abs(sigma12 + mu21[None, :, :]*sigma2)
        #     IFF_2 = np.where(
        #         (numerator > 0) & (S > 0),
        #         np.power(numerator / S, m),
        #         np.where(numerator == 0, 0, np.inf)
        #     )

        IFF_2 = np.nan_to_num(IFF_2, nan=0.0)


        # # Compute Reserve Factor (RF) for each failure mode
        # RF = (FF_1 + IFF_1 +IFF_2) ** (-1/m)
        # RF = np.where(RF == 0, np.inf, RF)  # Replace 0 with inf to avoid division by zero

        with np.errstate(divide='ignore', invalid='ignore'):
            sum_terms = FF_1 + IFF_1 + IFF_2
            RF = np.where(
                (sum_terms > 0) & np.isfinite(sum_terms),
                np.power(sum_terms, -1/m),
                np.where(sum_terms == 0, np.inf, np.nan)
            )


        self.RF_FMC_Tensor = RF # Store the RF tensor 

        return self.RF_FMC_Tensor # Shape: (Load Cases, Elements, Plies, 1)
# -----------------------------------------------------------------------------------------------------------------------------



# ---------------------------------------------- PLY-BY-PLY METHOD ------------------------------------------------------------    
    # @profile
    def check_plies(self, RFs):
        """
        Checks plies for failure based on the Reserve Factor (RF) values.
        
        This method iterates through the RF values and checks if any ply has failed (RF < 1).
        
        It creates a mask tensor with the same shape as the Stress_Array indicating which plies are active (RF >= 1) and returns it.

        Active plies will be assigned a float value of 1, while deactivated plies will be assigned a float value of 0.

        This method is pretended to be used in the PBP_vector method, therefore iteratively. Only the minimum RF < 1 will be considered as a failure. The mask will be updated accordingly in each iteration.

        The mask will be used to filter out the deactivated plies in further calculations, such as Qmatrix and QBar calculations.

        The method assumes that all plies are active at the beginning of the analysis and deactivates them based on the RF values.
         
        Args:
            RFs (np.ndarray): The Reserve Factor tensor for each load case, element, and ply. Shape: (Load Cases, Elements, Plies).
        
        Returns:
            np.ndarray: A masking tensor for each load case, element, and ply. Shape: (Load Cases, Elements, Plies).

        """
        # # Initialize the mask tensor with all plies active (1.0)
        # self.mask = np.ones_like(RFs, dtype=float)  # Shape: (Load Cases, Elements, Plies)  
        
        # # Iterate through LC and elements, and look for minimum RF at each element
        # for l in range(RFs.shape[0]):  # over LoadCases
        #     for e in range(RFs.shape[1]):  # over Elements
        #         # Find the minimum RF for the current element across all plies
        #         min_RF = np.nanmin(RFs[l, e, :])  # Minimum RF for the element
        #         if min_RF < 1:  # If any ply has failed
        #             # Find the index of the critical ply (minimum RF)
        #             critical_ply_idx = np.nanargmin(RFs[l, e, :])  # Index of the critical ply
        #             # Deactivate the critical ply by setting its mask value to 0.0
        #             self.mask[l, e, critical_ply_idx] = 0.0  # Deactivate the failing ply
        #         else:
        #             continue  # If no ply has failed, keep all plies active
        # # Return the mask tensor

        # Initialize mask array
        self.mask = np.ones_like(RFs, dtype=float)
        
        # Find minimum RFs per element
        min_RFs = np.nanmin(RFs, axis=2)  # Shape: (LoadCases, Elements)
        
        # Find indices of critical plies
        critical_indices = np.nanargmin(RFs, axis=2)  # Shape: (LoadCases, Elements)
        
        # Create mask for failing elements
        failing_mask = min_RFs < 1  # Shape: (LoadCases, Elements)
        
        # Create index arrays for mask update
        lc_idx, elem_idx = np.where(failing_mask)
        ply_idx = critical_indices[failing_mask]
        
        # Update mask in single operation
        self.mask[lc_idx, elem_idx, ply_idx] = 0.0
        
        return self.mask  # Shape: (Load Cases, Elements, Plies)
    
    # @profile
    def deactivate_plies(self, mask):
        """
        This method deactivates plies. It does it using Mask tensor. When a ply has a 0 value in the mask tensor, it means that the ply is deactivated. 

        When a ply fails, it affects the overall stiffness of the lamiante, therefore it is necessary to deactivate it from the calculations. 

        The method iterates through mask tensor and switches to zero the components of the Q matrix for the correspondant ply.

        It is pretended to be used in the PBP_vector method, therefore iteratively. Only the minimum RF < 1 will be considered as a failure. The mask will be updated accordingly in each iteration.

        It is assumed that the mask tensor is already computed and available in the class instance.

        Returns:
            None: The method updates the Q matrix for each ply in the elements based on the mask tensor.
        """
        Q_Matrix = self.QMatrix_array  # Shape: (Elements, Plys, 9)
        Q_Bar = self.QBar_array  # Shape: (Elements, Plys, 9)

        # # Iterate through each element and ply to deactivate plies based on the mask
        # for l in range(mask.shape[0]):
        #     for e in range(mask.shape[1]):
        #         for p in range(mask.shape[2]):
        #             if mask[l, e, p] == 0.0:
        #                 # Deactivate the ply by setting its Q matrix components to zero
        #                 Q_Matrix[l, e, p, :] = 0.0  # Set Q matrix components to zero
        #                 Q_Bar[l, e, p, :] = 0.0
        #             else:
        #                 continue  # If the ply is active, keep its Q matrix components unchanged

        # Get indices where mask is 0
        failing_mask = (mask == 0.0)
        
        # Zero out Q matrices in single operation
        Q_Matrix[failing_mask] = 0.0
        Q_Bar[failing_mask] = 0.0

        return Q_Matrix, Q_Bar
    
    # @profile
    def PBP(self):
        """
        Performs the Ply-by-ply analysis (PBP) for compostie materials.
        
        Method begins with an initial calculation of the reserve factor (RF) usign the failure criteria selected by the user.
        
        It then iteratively checks for plies that have failed (RF < 1) and deactivates them in an auxiliary tensor that works as a mask.
        
        Mask is used to filter out the deactivated - failed - plies in further calcuations, such as ABD matrix. Failed plies are assumed to have zero stiffness, therefore its Qmatrix and Qbar matrix are set to zero, which will make an impact in the overall ABD Matrix of the laminate.
        
        The method continues until no more plies fail, or the maximum number of iterations is reached.
        
        returns:
            Initial_Results (np.ndarray): An array containing the initial reserve factors for each load case, element, and ply. Shape: (Load Cases, Elements, Plys).
            Failure_Results (np.ndarray): An array containing the summary of the analysis. If all plies fail, it will contain the RF of the first ply which fails and the lamina number. If laminate does not fail, it will contain the lowest RF of the healthy plies of the laminate (RF > 1) and the lamina number.
            Order_Results (np.ndarray): An array containing the minimum RF of the laminate in each iteration and the iteration number. This is used to track the progress of the analysis.
            
        """

        # Initialization
        # self.Composite_Shells = list(self._properties_elem.values())
        n_loadcases = len(self.LoadCases)
        n_elements = len(self.Elements)
        n_plies = max(len(shell.Laminate) for shell in self.Composite_Shells)
        
        # Initial Computation  
        if self.FailureTheory == "TsaiWu":
            TsaiWu_tensor = self.coeffs_TsaiWu(self.Allowables_tensor)  # Compute Tsai-Wu coefficients
            RFs_initial = self.compute_TsaiWu(self.Initial_Stresses, TsaiWu_tensor)  # Compute initial RFs using Tsai-Wu failure theory
        elif self.FailureTheory == "MaxStress":
            RFs_initial = self.compute_MaxStress(self.Initial_Stresses, self.Allowables_tensor)  # Compute initial RFs using Max Stress failure theory
        elif self.FailureTheory == "TsaiHill":
            RFs_initial = self.compute_TsaiHill(self.Initial_Stresses, self.Allowables_tensor)  # Compute initial RFs using Tsai-Hill failure theory
        elif self.FailureTheory == "FMC":
            FMC_tensor = self.coeffs_FMC()  # Compute Tsai-Wu coefficients
            RFs_initial = self.compute_FMC(self.Initial_Stresses, self.Allowables_tensor, FMC_tensor) # Compute initial RFs using FMC failure theory

        # elif self.FailureTheory == "Hashin":
        #     RFs_initial = self.compute_Hashin(self.Initial_Stresses, self.Allowables_tensor)
        # elif self.FailureTheory == "Puck":
        #     RFs_initial = self.compute_Puck(self.Initial_Stresses, self.Allowables_tensor)

        else:
            raise ValueError(f"Failure Theory {self.FailureTheory} is not implemented for PlyByPly criteria.")
        
        # Initialize failure control variable
        failure = np.any(np.logical_and(~np.isnan(RFs_initial), RFs_initial < 1))
        iteration = 1
        iteration_results = RFs_initial
        RFs = np.full((n_loadcases, n_elements, n_plies), np.inf)
        min_mask = np.nanmin(iteration_results, axis=-1, keepdims=True)
        RFs = np.where(iteration_results == min_mask, iteration_results, RFs)

        # Initialize result arrays
        self.Initial_Results = RFs_initial
        self.Failure_Results = np.full((n_loadcases, n_elements, 2), np.nan, dtype=object)  # [RF_fiber, ply_fiber, RF_matrix, ply_matrix]
        self.Order_Results = np.zeros((n_loadcases, n_elements, n_plies, 2), dtype=object)  # [RF, iteration]
        self.Order_Results[..., 0] = np.nan  # RF values as float
        self.Order_Results[..., 1] = np.nan  # Iteration numbers will be integers

        while failure and iteration <= n_plies:

            if iteration == 1:
                # Order_Results
                for l in range(n_loadcases):
                    for e in range(n_elements):
                        for p in range(n_plies):
                            if not iteration_results[l, e, p] == np.inf :
                                self.Order_Results[l, e, p, 0] = iteration_results[l, e, p]
                                if iteration_results[l, e, p] < 1:
                                    self.Order_Results[l, e, p, 1] = iteration
                                else:
                                    self.Order_Results[l, e, p, 1] = 0

                iteration += 1
            else:
                pass
            
            # Create a mask to check plies based on the initial RFs
            mask = self.check_plies(iteration_results)  # Create a mask tensor based on the initial RFs

            # Filter out deactivated plies. Update QMatrix and QBar based on the mask. Compute ABD matrix and stresses with the updated QBar.
            updated_QMatrix, updated_QBar = self.deactivate_plies(mask)  # Deactivate plies based on the mask
            updated_ABDMatrix = self.ABD_tensor(updated_QBar)  # Recompute ABD matrix with updated QBar
            Stresses = self.forces_stresses(self.Forces, updated_ABDMatrix, updated_QMatrix)  # Recompute stresses with updated ABD matrix
            
            # Compute RFs with the updated stresses
            if self.FailureTheory == "TsaiWu":
                iteration_results = self.compute_TsaiWu(Stresses, TsaiWu_tensor)  # Recompute RFs after deactivating plies
            if self.FailureTheory == "MaxStress":
                iteration_results = self.compute_MaxStress(Stresses, self.Allowables_tensor) # Recompute RFs after deactivating plies
            if self.FailureTheory == "TsaiHill":
                iteration_results = self.compute_TsaiHill(Stresses, self.Allowables_tensor)
            if self.FailureTheory == "FMC":
                iteration_results = self.compute_FMC(Stresses, self.Allowables_tensor, FMC_tensor)


            # Check if all values are inf for each (l,e) combination

            all_inf_mask = np.all(iteration_results == np.inf, axis=2)  # Shape: (l,e)

            # Get minimum values where not all inf
            min_RFs = np.where(
                ~all_inf_mask[..., np.newaxis],  # Expand for broadcasting
                np.nanmin(iteration_results, axis=2, keepdims=True),
                RFs
            )

            # Update RFs where we have valid minimums
            RFs = np.where(iteration_results == min_RFs, iteration_results, RFs)

            # Update Failure Condition
            failure = np.any(np.logical_and(~np.isnan(iteration_results), iteration_results < 1))
            
            # Print iteration summary
            # if failure:
            #     print(f"Iteration {iteration}: {np.sum(iteration_results < 1)} elements failed.")
            # else:
            #     print(f"Iteration {iteration}: No elements failed. Analysis completed.")


            # Create masks for valid and failing values
            valid_mask = ~np.isinf(iteration_results)
            failing_mask = (iteration_results < 1) & valid_mask
            
            # Update RF values (first column)
            self.Order_Results[..., 0] = np.where(valid_mask, iteration_results, self.Order_Results[..., 0])
            
            # Update iteration numbers (second column)
            self.Order_Results[..., 1] = np.where(failing_mask, iteration, 
                                                 np.where(valid_mask, 0, self.Order_Results[..., 1]))

            # Update iteration
            iteration += 1


        # Finalize Results. Overwrite RFs with the last iteration results. Ensuring to store healthy plies once the analysis is completed.
        RFs = np.where(RFs == np.inf, iteration_results, RFs)  # Fill NaNs with the last iteration results



        # Failure_Results
        if self.FailureTheory == "TsaiWu" or self.FailureTheory == "TsaiHill" or self.FailureTheory == "MaxStress" or self.FailureTheory == "FMC":
            for l in range(n_loadcases):
                for e in range(n_elements):
                    valid_values = ~np.isinf(RFs[l,e])

                    if np.all(RFs[l,e][valid_values] < 1):
                        self.Failure_Results[l, e, 0] = np.nanmin(RFs_initial[l, e])
                        self.Failure_Results[l, e, 1] = np.nanargmin(RFs_initial[l,e]) + 1  
                    if np.any(RFs[l,e][valid_values] > 1):
                        self.Failure_Results[l, e, 0] = np.nanmin(iteration_results[l,e])
                        self.Failure_Results[l, e, 1] = np.nanargmin(iteration_results[l,e]) + 1 
        else:
            for l in range(n_loadcases):
                for e in range(n_elements):
                    valid_values = ~np.isinf(RFs[l,e])

                    if np.all(np.logical_or(
                            self.Initial_Results[l,e,:,0][valid_values] < 1,
                            self.Initial_Results[l,e,:,2][valid_values] < 1
                        )):

                        self.Failure_Results[l, e, 0] = np.nanmin(RFs_initial[l, e, :, 0])
                        self.Failure_Results[l, e, 1] = np.nanargmin(RFs_initial[l,e,:, 0]) + 1  
                        self.Failure_Results[l, e, 2] = np.nanmin(RFs_initial[l, e, :, 2])
                        self.Failure_Results[l, e, 3] = np.nanargmin(RFs_initial[l,e,:, 2]) + 1

                    if np.any(np.logical_or(
                            self.Initial_Results[0,0,:,0][valid_values] > 1,
                            self.Initial_Results[0,0,:,2][valid_values] > 1
                        )):

                        self.Failure_Results[l, e, 0] = np.nanmin(iteration_results[l,e,:, 0])
                        self.Failure_Results[l, e, 1] = np.nanargmin(iteration_results[l,e,:, 0]) + 1 
                        self.Failure_Results[l, e, 2] = np.nanmin(iteration_results[l,e,:, 2])
                        self.Failure_Results[l, e, 3] = np.nanargmin(iteration_results[l,e,:, 2]) + 1


        # Avoid Infinite values in the results for data visualization
        self.Initial_Results = np.where(self.Initial_Results == np.inf, np.nan, self.Initial_Results)
        self.Failure_Results = np.where(self.Failure_Results == np.inf, np.nan, self.Failure_Results)
        self.Order_Results = np.where(self.Order_Results == np.inf, np.nan, self.Order_Results)
        
        return self.Initial_Results, self.Failure_Results, self.Order_Results


    def calculate(self):
        """ Select and performs the failure criterion calculation based on the user-specified type."""
        
        # Initialization
        self.Composite_Shells = list(self._properties_elem.values())
        n_loadcases = len(self.LoadCases)
        n_elements = len(self.Elements)
        n_plies = max(len(shell.Laminate) for shell in self.Composite_Shells)

        # Initialize result arrays
        if self.FailureTheory == "TsaiWu" or self.FailureTheory == "TsaiHill" or self.FailureTheory == "MaxStress" or self.FailureTheory == "FMC":
            self.Initial_Results = np.full((n_loadcases, n_elements, n_plies), np.inf)
            self.Failure_Results = np.full((n_loadcases, n_elements, 2), np.nan, dtype=object)  # [RF_fiber, ply_fiber]
            self.Order_Results = np.zeros((n_loadcases, n_elements, n_plies, 2), dtype=object)  # [RF, iteration]
            self.Order_Results[..., 0] = np.nan  # RF values as float
            self.Order_Results[..., 1] = np.nan  # Iteration numbers will be integers
        else:
            self.Initial_Results = np.full((n_loadcases, n_elements, n_plies, 2), np.inf)
            self.Failure_Results = np.full((n_loadcases, n_elements, 4), np.nan, dtype=object)  # [RF_fiber, ply_fiber, RF_matrix, ply_matrix]
            self.Order_Results = np.zeros((n_loadcases, n_elements, n_plies, 4), dtype=object)  # [RF, iteration]
            self.Order_Results[..., 0] = np.nan  # RF_fiber values as float
            self.Order_Results[..., 1] = np.nan  # Iteration numbers will be integers
            self.Order_Results[..., 2] = np.nan  # RF_matrix values as float
            self.Order_Results[..., 3] = np.nan  # Iteration numbers for matrix failure will be integers

        # Step 0: Extract forces. Compute Q, QBar, ABD matrices, and stresses.
        self.Forces = self.forces_tensor()
        # print("Forces tensor computed.")
        self.QMatrix, self.QBar = self.Q_tensor()
        # print("Q tensor computed.")
        self.Allowables = self.allowables_tensor()  # Shape: (Elements, Plys, 5)
        # print("Allowables tensor computed.")

        #Step 0.1: Initialize variables for the computation of ABD Matrix. These varaibles are common throughout the analysi, therefore it is necessary to precompute them to avoid redundant computations through the iterations.
        # Initialize thickness arrays using vectorization
        self.thicknesses = np.zeros((n_elements, n_plies), dtype= np.float64)
        for i, shell in enumerate(self.Composite_Shells):
            self.thicknesses[i, :len(shell.Laminate)] = [ply.thickness for ply in shell.Laminate]
        # print("Thicknesses tensor computed.")
        # Compute total thickness and lower reference
        total_thickness = np.sum(self.thicknesses, axis=1, keepdims=True)
        lower_ref = -total_thickness / 2

        # create a numpy array to store the centroid of each lamina on each element with regard to lower reference. Shape (n_elements, n_plies)
        # Initialize centroid array
        self.centroid = np.zeros((n_elements, n_plies), dtype=np.float64)

        # Calculate cumulative thicknesses
        cumulative_thickness = np.cumsum(self.thicknesses, axis=1)

        # Squeeze extra dimension from lower_ref
        lower_ref = lower_ref.squeeze()  # Shape: (15839,)

        # Compute all centroids at once using broadcasting
        half_thickness = self.thicknesses / 2
        self.centroid = lower_ref[:, np.newaxis] + cumulative_thickness - half_thickness
        # print("Centroid tensor computed.")



        # Step 1: Initial Computation.
        self.Initial_ABDMatrix = self.ABD_tensor(self.QBar)  # Compute ABD matrix for all elements and load cases
        self.Initial_Stresses = self.forces_stresses(self.Forces, self.Initial_ABDMatrix, self.QMatrix) # Compute stresses for all elements and load cases
        
        if self.FailureCriteria == "FirstPly":
            if self.FailureTheory == "TsaiWu":
                self.TsaiWu_tensor = self.coeffs_TsaiWu(self.Allowables)  # Compute Tsai-Wu coefficients
                self.Initial_Results = self.compute_TsaiWu(self.Initial_Stresses, self.TsaiWu_tensor)  # Compute initial RFs using Tsai-Wu failure theory
            if self.FailureTheory == "MaxStress":
                self.Initial_Results = self.compute_MaxStress(self.Initial_Stresses, self.Allowables)
            if self.FailureTheory == "TsaiHill":
                self.Initial_Results = self.compute_TsaiHill(self.Initial_Stresses, self.Allowables)
            if self.FailureTheory == "Hashin":
                self.Initial_Results = self.compute_Hashin(self.Initial_Stresses, self.Allowables)
            if self.FailureTheory == "Puck":
                self.Initial_Results = self.compute_Puck(self.Initial_Stresses, self.Allowables)
            if self.FailureTheory == "FMC":
                self.FMC_tensor = self.coeffs_FMC()
                # Compute FMC coefficients
                self.Initial_Results = self.compute_FMC(self.Initial_Stresses, self.Allowables, self.FMC_tensor)
                # Compute initial RFs using FMC failure theory


            # Failure_Results
            if self.FailureTheory == "TsaiWu" or self.FailureTheory == "MaxStress" or self.FailureTheory == "TsaiHill" or self.FailureTheory == "FMC":
                for l in range(n_loadcases):
                    for e in range(n_elements):
                        valid_values = ~np.isinf(self.Initial_Results[l,e])

                        if np.all(self.Initial_Results[0,0][valid_values] < 1):
                            self.Failure_Results[l, e, 0] = np.nanmin(self.Initial_Results[l, e])
                            self.Failure_Results[l, e, 1] = np.nanargmin(self.Initial_Results[l,e]) + 1  
                        if np.any(self.Initial_Results[0,0][valid_values] > 1):
                            self.Failure_Results[l, e, 0] = np.nanmin(self.Initial_Results[l,e])
                            self.Failure_Results[l, e, 1] = np.nanargmin(self.Initial_Results[l,e]) + 1
            else:
                for l in range(n_loadcases):
                    for e in range(n_elements):
                        valid_values = ~np.isinf(self.Initial_Results[l,e,:,0])

                        if np.all(np.logical_or(
                            self.Initial_Results[0,0,:,0][valid_values] < 1,
                            self.Initial_Results[0,0,:,1][valid_values] < 1
                        )):
                            self.Failure_Results[l, e, 0] = np.nanmin(self.Initial_Results[l, e,:,0])
                            self.Failure_Results[l, e, 1] = np.nanargmin(self.Initial_Results[l,e,:,0]) + 1
                            self.Failure_Results[l, e, 2] = np.nanmin(self.Initial_Results[l, e,:,1])
                            self.Failure_Results[l, e, 3] = np.nanargmin(self.Initial_Results[l,e,:,1]) + 1  
                        if np.any(np.logical_or(
                            self.Initial_Results[0,0,:,0][valid_values] > 1,
                            self.Initial_Results[0,0,:,1][valid_values] > 1
                        )):
                            self.Failure_Results[l, e, 0] = np.nanmin(self.Initial_Results[l,e,:,0])
                            self.Failure_Results[l, e, 1] = np.nanargmin(self.Initial_Results[l,e,:,0]) + 1
                            self.Failure_Results[l, e, 2] = np.nanmin(self.Initial_Results[l,e,:,1])
                            self.Failure_Results[l, e, 3] = np.nanargmin(self.Initial_Results[l,e,:,1]) + 1


        elif self.FailureCriteria == "PlyByPly":
            self.Initial_Results, self.Failure_Results, self.Order_Results = self.PBP()  # Perform Ply-by-Ply analysis

        # Avoid Infinite values in the results for data visualization
        self.Initial_Results = np.where(self.Initial_Results == np.inf, np.nan, self.Initial_Results)
        self.Failure_Results = np.where(self.Failure_Results == np.inf, np.nan, self.Failure_Results)
        self.Order_Results = np.where(self.Order_Results == np.inf, np.nan, self.Order_Results)

        return self._transform_results(self.LoadCases)

# # -----------------------------------------------------------------------------------------------------------------------------
    
    # @profile
    def _extract_forces(self, LC):

        """
        Method to extract Forces results from N2PModelContent. Differentiates between the different solvers
        supported by NaxToPy.

        Returns a dictionary that store the planar forces and moments (global axis orientation) for each
        section (ply) of the element.

            Forces_element = {N2PElement : [Fx, Fy, Fz, Mx, My, Mz]}



        """
        # Dictionary initialisation -------------------------------------------------------------------------------------------

        
        self.sections_Fx = {}
        self.sections_Fy = {}
        self.sections_Fxy = {}
        self.sections_Mx = {}
        self.sections_My = {}
        self.sections_Mxy = {}


        # Extraction of stress results on all the elements --------------------------------------------------------------------
        if self._model.Solver == 'Nastran' or self._model.Solver == 'Optistruct' or self._model.Solver == 'InputFileNastran':
            results = 'FORCES'
            componentFx = 'FX'
            componentFy = 'FY'
            componentFxy = 'FXY'
            componentMx = 'MX'
            componentMy = 'MY'
            componentMxy = 'MXY'
        
        # elif self._model.Solver == 'Abaqus':
        #     componentFx = 'FX'
        #     componentFy = 'FY'
        #     componentFz = 'FZ'
        #     componentMx = 'MX'
        #     componentMy = 'MY'
        #     componentMz = 'MZ'
        
        # elif self._model.Solver == 'Ansys':
        #     componentFx = 'FX'
        #     componentFy = 'FY'
        #     componentFz = 'FZ'
        #     componentMx = 'MX'
        #     componentMy = 'MY'
        #     componentMz = 'MZ'


        self.sections_results_Fx = LC.get_result(results).get_component(componentFx).Sections
        self.sections_results_Fy = LC.get_result(results).get_component(componentFy).Sections
        self.sections_results_Fxy = LC.get_result(results).get_component(componentFxy).Sections
        self.sections_results_Mx = LC.get_result(results).get_component(componentMx).Sections
        self.sections_results_My = LC.get_result(results).get_component(componentMy).Sections
        self.sections_results_Mxy = LC.get_result(results).get_component(componentMxy).Sections
        for sectionFx, sectionFy, sectionFxy, sectionMx, sectionMy, sectionMxy in zip(self.sections_results_Fx, self.sections_results_Fy, self.sections_results_Fxy,self.sections_results_Mx, self.sections_results_My, self.sections_results_Mxy):
            self.sections_Fx[sectionFx] = LC.get_result(results).get_component(componentFx).get_result_array([sectionFx.Name])[0]
            self.sections_Fy[sectionFy] = LC.get_result(results).get_component(componentFy).get_result_array([sectionFy.Name])[0]
            self.sections_Fxy[sectionFxy] = LC.get_result(results).get_component(componentFxy).get_result_array([sectionFxy.Name])[0]
            self.sections_Mx[sectionMx] = LC.get_result(results).get_component(componentMx).get_result_array([sectionMx.Name])[0]
            self.sections_My[sectionMy] = LC.get_result(results).get_component(componentMy).get_result_array([sectionMy.Name])[0]
            self.sections_Mxy[sectionMxy] = LC.get_result(results).get_component(componentMxy).get_result_array([sectionMxy.Name])[0]


        # Apply filter to acquire results at just the elements selected by user ------------------------------------------------

        index = [elem.InternalID for elem in self._element_list]

        for sectionFx, sectionFy, sectionFxy, sectionMx, sectionMy, sectionMxy in zip(self.sections_results_Fx, self.sections_results_Fy, self.sections_results_Fxy,self.sections_results_Mx, self.sections_results_My, self.sections_results_Mxy):
            self.sections_Fx[sectionFx] = [self.sections_Fx[sectionFx][i] for i in index]
            self.sections_Fy[sectionFy] = [self.sections_Fy[sectionFy][i] for i in index]
            self.sections_Fxy[sectionFxy] = [self.sections_Fxy[sectionFxy][i] for i in index]
            self.sections_Mx[sectionMx] = [self.sections_Mx[sectionMx][i] for i in index]
            self.sections_My[sectionMy] = [self.sections_My[sectionMy][i] for i in index]
            self.sections_Mxy[sectionMxy] = [self.sections_Mxy[sectionMxy][i] for i in index]

        # Create Dictionary to relate forces in different laminaes to its respective N2PElement instance ------------------------
        
        # Dictionary initialization ---------------------------------------------------------------------------------------------
        self.Fx_element = {n2p_element: [] for n2p_element in self._element_list}
        self.Fy_element = {n2p_element: [] for n2p_element in self._element_list}    
        self.Fxy_element = {n2p_element: [] for n2p_element in self._element_list}        
        self.Mx_element = {n2p_element: [] for n2p_element in self._element_list}
        self.My_element = {n2p_element: [] for n2p_element in self._element_list}    
        self.Mxy_element = {n2p_element: [] for n2p_element in self._element_list} 

        Forces_element = {n2p_element: [] for n2p_element in self._element_list}   

        # Read the list of elements obtained from user input -------------------------------------------------------------------- 
        for i in range(len(self._element_list)):
            # Acquiring N2PElement instance -------------------------------------------------------------------------------------                                         
            n2p_element = self._element_list[i] 
            # List to temporaly store forces on each element --------------------------------------------------------------------                                   
            Fx_values = []
            Fy_values = []
            Fxy_values = []
            Mx_values = []
            My_values = []
            Mxy_values = []
            Forces = []

            #Go through the sections and obtain the corresponding forces for this element ---------------------------------------                                                       
            for section in self.sections_Fx.keys():     
                Fx_values.append(self.sections_Fx[section][i])
                Forces.append(self.sections_Fx[section][i])
            for section in self.sections_Fy.keys():
                Fy_values.append(self.sections_Fy[section][i])
                Forces.append(self.sections_Fy[section][i])
            for section in self.sections_Fxy.keys():
                Fxy_values.append(self.sections_Fxy[section][i])
                Forces.append(self.sections_Fxy[section][i])
            for section in self.sections_Mx.keys():     
                Mx_values.append(self.sections_Mx[section][i])
                Forces.append(self.sections_Mx[section][i])
            for section in self.sections_My.keys():
                My_values.append(self.sections_My[section][i])
                Forces.append(self.sections_My[section][i])
            for section in self.sections_Mxy.keys():
                Mxy_values.append(self.sections_Mxy[section][i])
                Forces.append(self.sections_Mxy[section][i])

            # Assign the stresses list to the N2PElement in the stress_element dictionary --------------------------------------
            self.Fx_element[n2p_element] = Fx_values
            self.Fy_element[n2p_element] = Fy_values
            self.Fxy_element[n2p_element] = Fxy_values
            self.Mx_element[n2p_element] = Mx_values
            self.My_element[n2p_element] = My_values
            self.Mxy_element[n2p_element] = Mxy_values

            Forces_element[n2p_element] = Forces
    
        
        return Forces_element 

    # @profile
    def _transform_results(self, List_LCs):
        """
        Method to transform a results dictionary into multiple Numpy array.

        This method also takes responsibility for results file creation into h5 type format.
        HDF5_NaxTo and DataEntry classes, and their methods, are imported and used for file creation.  
        
        Args:
            Analysis_Results (dict): Dictionary with N2PElement instances as keys, and RF:list as values.

        Returns: 
            datasets (list[np.array]): A list of Numpy arrays [ElementID, RF], one per section (layer). 
        """



        n_elements = len(self.Elements)
        n_plies = max(len(shell.Laminate) for shell in self.Composite_Shells)
        results_names = ['Initial_Results', 'Failure_Results', 'Order_Results']
        
        self.dataEntryList = []
        self._hdf5.create_hdf5()
    
        # Predefine data types
        dtype_map = {
            'default': [("ID ENTITY", "i4"), ("RF", "f4")],
            'Hashin_Puck': [("ID ENTITY", "i4"), ("RF_fiber", "f4"), ("RF_matrix", "f4")],
            'Failure_Default': [("ID ENTITY", "i4"), ("RF", "f4"), ("Lamina", "f4")],
            'Failure_Hashin_Puck': [("ID ENTITY", "i4"), ("RF_fiber", "f4"), ("Lamina_fiber", "f4"), ("RF_matrix", "f4"), ("Lamina_matrix", "f4")],
            'Order_Default': [("ID ENTITY", "i4"), ("RF", "f4"), ("Order", "f4")],
            'Order_Hashin_Puck': [("ID ENTITY", "i4"), ("RF_fiber", "f4"), ("Order_fiber", "f4"), ("RF_matrix", "f4"), ("Order_matrix", "f4")]
        }
    
        element_ids = np.array([e.ID for e in self.Elements], dtype=np.int32)

        if self.FailureCriteria == "FirstPly":
            for lc_idx, LC in enumerate(List_LCs):
                # Initialize structured arrays
                if self.FailureTheory in ['TsaiWu', 'TsaiHill', 'MaxStress', 'FMC']:
                    arrays_initial = np.zeros((n_plies, n_elements), dtype=dtype_map['default'])
                    array_failure = np.zeros(n_elements, dtype=dtype_map['Failure_Default'])
                else:
                    arrays_initial = np.zeros((n_plies, n_elements), dtype=dtype_map['Hashin_Puck'])
                    array_failure = np.zeros(n_elements, dtype=dtype_map['Failure_Hashin_Puck'])


                # Fill datasets
                if self.FailureTheory in ['TsaiWu', 'TsaiHill', 'MaxStress', 'FMC']:
                    # Initial_Results dataset.
                    for ply in range(n_plies):
                        arrays_initial[ply]['ID ENTITY'] = element_ids
                        arrays_initial[ply]['RF'] = self.Initial_Results[lc_idx, :, ply]
                    # Failure_Results dataset.
                    array_failure['ID ENTITY'] = element_ids
                    array_failure['RF'] = self.Failure_Results[lc_idx, :, 0]
                    array_failure['Lamina'] = self.Failure_Results[lc_idx, :, 1]
                else:
                    # Initial_Results dataset.
                    for ply in range(n_plies):
                        arrays_initial[ply]['ID ENTITY'] = element_ids
                        arrays_initial[ply]['RF_fiber'] = self.Initial_Results[lc_idx, :, ply, 0]
                        arrays_initial[ply]['RF_matrix'] = self.Initial_Results[lc_idx, :, ply, 1]
                    # Failure_Results dataset.
                    array_failure['ID ENTITY'] = element_ids
                    array_failure['RF_fiber'] = self.Failure_Results[lc_idx, :, 0]
                    array_failure['Lamina_fiber'] = self.Failure_Results[lc_idx, :, 1]
                    array_failure['RF_matrix'] = self.Failure_Results[lc_idx, :, 2]
                    array_failure['Lamina_matrix'] = self.Failure_Results[lc_idx, :, 3]

                datasets = [arrays_initial, array_failure]

                for i, dataset in enumerate(datasets):
                    result_name = results_names[i]

                    if i == 1:
                        # Store in HDF5
                        data_entry = DataEntry()
                        data_entry.LoadCase = LC.ID
                        data_entry.LoadCaseName = 'Load Case'
                        data_entry.Increment = LC.ActiveN2PIncrement.ID
                        data_entry.Data = dataset
                        data_entry.Section = "all"
                        data_entry.ResultsName = result_name
                        data_entry.Part = "(0,'0')"
                        self.dataEntryList.append(data_entry)
                    else:
                        for j in range(dataset.shape[0]):
                            data_entry = DataEntry()
                            data_entry.LoadCase = LC.ID
                            data_entry.LoadCaseName = 'Load Case'
                            data_entry.Increment = LC.ActiveN2PIncrement.ID
                            data_entry.Data = dataset[j] if i == 0 else dataset 
                            data_entry.Section = str(j)
                            data_entry.ResultsName = result_name
                            data_entry.Part = "(0,'0')"
                            self.dataEntryList.append(data_entry)

            
        
        elif self.FailureCriteria == "PlyByPly":    
        
            for lc_idx, LC in enumerate(List_LCs):
                # Create structured arrays
                arrays_initial = np.zeros((n_plies, n_elements), dtype=dtype_map['default'])
                array_failure = np.zeros(n_elements, dtype=dtype_map['Failure_Default'])
                arrays_order = np.zeros((n_plies, n_elements), dtype=dtype_map['Order_Default'])

                for ply in range(n_plies):
                    # Fill arrays
                    arrays_initial[ply]['ID ENTITY'] = element_ids
                    arrays_initial[ply]['RF'] = self.Initial_Results[lc_idx, :, ply]
                
                array_failure['ID ENTITY'] = element_ids
                array_failure['RF'] = self.Failure_Results[lc_idx, :, 0]
                array_failure['Lamina'] = self.Failure_Results[lc_idx, :, 1]
                
                for ply in range(n_plies):
                    arrays_order[ply]['ID ENTITY'] = element_ids
                    arrays_order[ply]['RF'] = self.Order_Results[lc_idx, :, ply, 0]
                    arrays_order[ply]['Order'] = self.Order_Results[lc_idx, :, ply, 1]
        
                # Store in HDF5
                datasets = [arrays_initial, array_failure, arrays_order]
                
                for i, dataset in enumerate(datasets):
                    result_name = results_names[i]
                    
                    if i == 1:  # Failure_Results
                        data_entry = DataEntry()
                        data_entry.LoadCase = LC.ID
                        data_entry.LoadCaseName = 'Load Case'
                        data_entry.Increment = LC.ActiveN2PIncrement.ID
                        data_entry.Data = dataset
                        data_entry.Section = 'all'
                        data_entry.ResultsName = result_name
                        data_entry.Part = "(0,'0')"
                        self.dataEntryList.append(data_entry)
                    else:  # Initial_Results and Order_Results
                        for j in range(dataset.shape[0]):
                            data_entry = DataEntry()
                            data_entry.LoadCase = LC.ID
                            data_entry.LoadCaseName = 'Load Case'
                            data_entry.Increment = LC.ActiveN2PIncrement.ID
                            data_entry.Data = dataset[j] if i == 0 or i == 2 else dataset 
                            data_entry.Section = str(j)
                            data_entry.ResultsName = result_name
                            data_entry.Part = "(0,'0')"
                            self.dataEntryList.append(data_entry)
        else:
            pass

        self._hdf5.write_dataset(self.dataEntryList)
        return None