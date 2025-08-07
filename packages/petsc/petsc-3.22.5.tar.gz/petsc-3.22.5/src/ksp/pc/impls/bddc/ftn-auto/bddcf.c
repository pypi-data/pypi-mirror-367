#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* bddc.c */
/* Fortran interface file */

/*
* This file was generated automatically by bfort from the C source
* file.  
 */

#ifdef PETSC_USE_POINTER_CONVERSION
#if defined(__cplusplus)
extern "C" { 
#endif 
extern void *PetscToPointer(void*);
extern int PetscFromPointer(void *);
extern void PetscRmPointer(void*);
#if defined(__cplusplus)
} 
#endif 

#else

#define PetscToPointer(a) (a ? *(PetscFortranAddr *)(a) : 0)
#define PetscFromPointer(a) (PetscFortranAddr)(a)
#define PetscRmPointer(a)
#endif

#include "petscpc.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcbddcsetdiscretegradient_ PCBDDCSETDISCRETEGRADIENT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcbddcsetdiscretegradient_ pcbddcsetdiscretegradient
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcbddcsetdivergencemat_ PCBDDCSETDIVERGENCEMAT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcbddcsetdivergencemat_ pcbddcsetdivergencemat
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcbddcsetchangeofbasismat_ PCBDDCSETCHANGEOFBASISMAT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcbddcsetchangeofbasismat_ pcbddcsetchangeofbasismat
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcbddcsetprimalverticesis_ PCBDDCSETPRIMALVERTICESIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcbddcsetprimalverticesis_ pcbddcsetprimalverticesis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcbddcgetprimalverticesis_ PCBDDCGETPRIMALVERTICESIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcbddcgetprimalverticesis_ pcbddcgetprimalverticesis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcbddcsetprimalverticeslocalis_ PCBDDCSETPRIMALVERTICESLOCALIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcbddcsetprimalverticeslocalis_ pcbddcsetprimalverticeslocalis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcbddcgetprimalverticeslocalis_ PCBDDCGETPRIMALVERTICESLOCALIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcbddcgetprimalverticeslocalis_ pcbddcgetprimalverticeslocalis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcbddcsetcoarseningratio_ PCBDDCSETCOARSENINGRATIO
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcbddcsetcoarseningratio_ pcbddcsetcoarseningratio
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcbddcsetlevels_ PCBDDCSETLEVELS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcbddcsetlevels_ pcbddcsetlevels
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcbddcsetdirichletboundaries_ PCBDDCSETDIRICHLETBOUNDARIES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcbddcsetdirichletboundaries_ pcbddcsetdirichletboundaries
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcbddcsetdirichletboundarieslocal_ PCBDDCSETDIRICHLETBOUNDARIESLOCAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcbddcsetdirichletboundarieslocal_ pcbddcsetdirichletboundarieslocal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcbddcsetneumannboundaries_ PCBDDCSETNEUMANNBOUNDARIES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcbddcsetneumannboundaries_ pcbddcsetneumannboundaries
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcbddcsetneumannboundarieslocal_ PCBDDCSETNEUMANNBOUNDARIESLOCAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcbddcsetneumannboundarieslocal_ pcbddcsetneumannboundarieslocal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcbddcgetdirichletboundaries_ PCBDDCGETDIRICHLETBOUNDARIES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcbddcgetdirichletboundaries_ pcbddcgetdirichletboundaries
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcbddcgetdirichletboundarieslocal_ PCBDDCGETDIRICHLETBOUNDARIESLOCAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcbddcgetdirichletboundarieslocal_ pcbddcgetdirichletboundarieslocal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcbddcgetneumannboundaries_ PCBDDCGETNEUMANNBOUNDARIES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcbddcgetneumannboundaries_ pcbddcgetneumannboundaries
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcbddcgetneumannboundarieslocal_ PCBDDCGETNEUMANNBOUNDARIESLOCAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcbddcgetneumannboundarieslocal_ pcbddcgetneumannboundarieslocal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcbddcsetlocaladjacencygraph_ PCBDDCSETLOCALADJACENCYGRAPH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcbddcsetlocaladjacencygraph_ pcbddcsetlocaladjacencygraph
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcbddcsetdofssplittinglocal_ PCBDDCSETDOFSSPLITTINGLOCAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcbddcsetdofssplittinglocal_ pcbddcsetdofssplittinglocal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcbddcsetdofssplitting_ PCBDDCSETDOFSSPLITTING
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcbddcsetdofssplitting_ pcbddcsetdofssplitting
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcbddcmatfetidpgetrhs_ PCBDDCMATFETIDPGETRHS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcbddcmatfetidpgetrhs_ pcbddcmatfetidpgetrhs
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcbddcmatfetidpgetsolution_ PCBDDCMATFETIDPGETSOLUTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcbddcmatfetidpgetsolution_ pcbddcmatfetidpgetsolution
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  pcbddcsetdiscretegradient_(PC pc,Mat G,PetscInt *order,PetscInt *field,PetscBool *global,PetscBool *conforming, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(G);
*ierr = PCBDDCSetDiscreteGradient(
	(PC)PetscToPointer((pc) ),
	(Mat)PetscToPointer((G) ),*order,*field,*global,*conforming);
}
PETSC_EXTERN void  pcbddcsetdivergencemat_(PC pc,Mat divudotp,PetscBool *trans,IS vl2l, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(divudotp);
CHKFORTRANNULLOBJECT(vl2l);
*ierr = PCBDDCSetDivergenceMat(
	(PC)PetscToPointer((pc) ),
	(Mat)PetscToPointer((divudotp) ),*trans,
	(IS)PetscToPointer((vl2l) ));
}
PETSC_EXTERN void  pcbddcsetchangeofbasismat_(PC pc,Mat change,PetscBool *interior, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(change);
*ierr = PCBDDCSetChangeOfBasisMat(
	(PC)PetscToPointer((pc) ),
	(Mat)PetscToPointer((change) ),*interior);
}
PETSC_EXTERN void  pcbddcsetprimalverticesis_(PC pc,IS PrimalVertices, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(PrimalVertices);
*ierr = PCBDDCSetPrimalVerticesIS(
	(PC)PetscToPointer((pc) ),
	(IS)PetscToPointer((PrimalVertices) ));
}
PETSC_EXTERN void  pcbddcgetprimalverticesis_(PC pc,IS *is, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
PetscBool is_null = !*(void**) is ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(is);
*ierr = PCBDDCGetPrimalVerticesIS(
	(PC)PetscToPointer((pc) ),is);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! is_null && !*(void**) is) * (void **) is = (void *)-2;
}
PETSC_EXTERN void  pcbddcsetprimalverticeslocalis_(PC pc,IS PrimalVertices, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(PrimalVertices);
*ierr = PCBDDCSetPrimalVerticesLocalIS(
	(PC)PetscToPointer((pc) ),
	(IS)PetscToPointer((PrimalVertices) ));
}
PETSC_EXTERN void  pcbddcgetprimalverticeslocalis_(PC pc,IS *is, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
PetscBool is_null = !*(void**) is ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(is);
*ierr = PCBDDCGetPrimalVerticesLocalIS(
	(PC)PetscToPointer((pc) ),is);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! is_null && !*(void**) is) * (void **) is = (void *)-2;
}
PETSC_EXTERN void  pcbddcsetcoarseningratio_(PC pc,PetscInt *k, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCBDDCSetCoarseningRatio(
	(PC)PetscToPointer((pc) ),*k);
}
PETSC_EXTERN void  pcbddcsetlevels_(PC pc,PetscInt *levels, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCBDDCSetLevels(
	(PC)PetscToPointer((pc) ),*levels);
}
PETSC_EXTERN void  pcbddcsetdirichletboundaries_(PC pc,IS DirichletBoundaries, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(DirichletBoundaries);
*ierr = PCBDDCSetDirichletBoundaries(
	(PC)PetscToPointer((pc) ),
	(IS)PetscToPointer((DirichletBoundaries) ));
}
PETSC_EXTERN void  pcbddcsetdirichletboundarieslocal_(PC pc,IS DirichletBoundaries, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(DirichletBoundaries);
*ierr = PCBDDCSetDirichletBoundariesLocal(
	(PC)PetscToPointer((pc) ),
	(IS)PetscToPointer((DirichletBoundaries) ));
}
PETSC_EXTERN void  pcbddcsetneumannboundaries_(PC pc,IS NeumannBoundaries, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(NeumannBoundaries);
*ierr = PCBDDCSetNeumannBoundaries(
	(PC)PetscToPointer((pc) ),
	(IS)PetscToPointer((NeumannBoundaries) ));
}
PETSC_EXTERN void  pcbddcsetneumannboundarieslocal_(PC pc,IS NeumannBoundaries, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(NeumannBoundaries);
*ierr = PCBDDCSetNeumannBoundariesLocal(
	(PC)PetscToPointer((pc) ),
	(IS)PetscToPointer((NeumannBoundaries) ));
}
PETSC_EXTERN void  pcbddcgetdirichletboundaries_(PC pc,IS *DirichletBoundaries, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
PetscBool DirichletBoundaries_null = !*(void**) DirichletBoundaries ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(DirichletBoundaries);
*ierr = PCBDDCGetDirichletBoundaries(
	(PC)PetscToPointer((pc) ),DirichletBoundaries);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! DirichletBoundaries_null && !*(void**) DirichletBoundaries) * (void **) DirichletBoundaries = (void *)-2;
}
PETSC_EXTERN void  pcbddcgetdirichletboundarieslocal_(PC pc,IS *DirichletBoundaries, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
PetscBool DirichletBoundaries_null = !*(void**) DirichletBoundaries ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(DirichletBoundaries);
*ierr = PCBDDCGetDirichletBoundariesLocal(
	(PC)PetscToPointer((pc) ),DirichletBoundaries);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! DirichletBoundaries_null && !*(void**) DirichletBoundaries) * (void **) DirichletBoundaries = (void *)-2;
}
PETSC_EXTERN void  pcbddcgetneumannboundaries_(PC pc,IS *NeumannBoundaries, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
PetscBool NeumannBoundaries_null = !*(void**) NeumannBoundaries ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(NeumannBoundaries);
*ierr = PCBDDCGetNeumannBoundaries(
	(PC)PetscToPointer((pc) ),NeumannBoundaries);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! NeumannBoundaries_null && !*(void**) NeumannBoundaries) * (void **) NeumannBoundaries = (void *)-2;
}
PETSC_EXTERN void  pcbddcgetneumannboundarieslocal_(PC pc,IS *NeumannBoundaries, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
PetscBool NeumannBoundaries_null = !*(void**) NeumannBoundaries ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(NeumannBoundaries);
*ierr = PCBDDCGetNeumannBoundariesLocal(
	(PC)PetscToPointer((pc) ),NeumannBoundaries);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! NeumannBoundaries_null && !*(void**) NeumannBoundaries) * (void **) NeumannBoundaries = (void *)-2;
}
PETSC_EXTERN void  pcbddcsetlocaladjacencygraph_(PC pc,PetscInt *nvtxs, PetscInt xadj[], PetscInt adjncy[],PetscCopyMode *copymode, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLINTEGER(xadj);
CHKFORTRANNULLINTEGER(adjncy);
*ierr = PCBDDCSetLocalAdjacencyGraph(
	(PC)PetscToPointer((pc) ),*nvtxs,xadj,adjncy,*copymode);
}
PETSC_EXTERN void  pcbddcsetdofssplittinglocal_(PC pc,PetscInt *n_is,IS ISForDofs[], int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
PetscBool ISForDofs_null = !*(void**) ISForDofs ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(ISForDofs);
*ierr = PCBDDCSetDofsSplittingLocal(
	(PC)PetscToPointer((pc) ),*n_is,ISForDofs);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! ISForDofs_null && !*(void**) ISForDofs) * (void **) ISForDofs = (void *)-2;
}
PETSC_EXTERN void  pcbddcsetdofssplitting_(PC pc,PetscInt *n_is,IS ISForDofs[], int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
PetscBool ISForDofs_null = !*(void**) ISForDofs ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(ISForDofs);
*ierr = PCBDDCSetDofsSplitting(
	(PC)PetscToPointer((pc) ),*n_is,ISForDofs);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! ISForDofs_null && !*(void**) ISForDofs) * (void **) ISForDofs = (void *)-2;
}
PETSC_EXTERN void  pcbddcmatfetidpgetrhs_(Mat fetidp_mat,Vec standard_rhs,Vec fetidp_flux_rhs, int *ierr)
{
CHKFORTRANNULLOBJECT(fetidp_mat);
CHKFORTRANNULLOBJECT(standard_rhs);
CHKFORTRANNULLOBJECT(fetidp_flux_rhs);
*ierr = PCBDDCMatFETIDPGetRHS(
	(Mat)PetscToPointer((fetidp_mat) ),
	(Vec)PetscToPointer((standard_rhs) ),
	(Vec)PetscToPointer((fetidp_flux_rhs) ));
}
PETSC_EXTERN void  pcbddcmatfetidpgetsolution_(Mat fetidp_mat,Vec fetidp_flux_sol,Vec standard_sol, int *ierr)
{
CHKFORTRANNULLOBJECT(fetidp_mat);
CHKFORTRANNULLOBJECT(fetidp_flux_sol);
CHKFORTRANNULLOBJECT(standard_sol);
*ierr = PCBDDCMatFETIDPGetSolution(
	(Mat)PetscToPointer((fetidp_mat) ),
	(Vec)PetscToPointer((fetidp_flux_sol) ),
	(Vec)PetscToPointer((standard_sol) ));
}
#if defined(__cplusplus)
}
#endif
