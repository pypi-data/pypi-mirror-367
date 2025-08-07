#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* hypre.c */
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
#define pchypresetdiscretegradient_ PCHYPRESETDISCRETEGRADIENT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pchypresetdiscretegradient_ pchypresetdiscretegradient
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pchypresetdiscretecurl_ PCHYPRESETDISCRETECURL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pchypresetdiscretecurl_ pchypresetdiscretecurl
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pchypresetinterpolations_ PCHYPRESETINTERPOLATIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pchypresetinterpolations_ pchypresetinterpolations
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pchypresetalphapoissonmatrix_ PCHYPRESETALPHAPOISSONMATRIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pchypresetalphapoissonmatrix_ pchypresetalphapoissonmatrix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pchypresetbetapoissonmatrix_ PCHYPRESETBETAPOISSONMATRIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pchypresetbetapoissonmatrix_ pchypresetbetapoissonmatrix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pchypresetedgeconstantvectors_ PCHYPRESETEDGECONSTANTVECTORS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pchypresetedgeconstantvectors_ pchypresetedgeconstantvectors
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pchypreamssetinteriornodes_ PCHYPREAMSSETINTERIORNODES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pchypreamssetinteriornodes_ pchypreamssetinteriornodes
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pchypresettype_ PCHYPRESETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pchypresettype_ pchypresettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pchypregettype_ PCHYPREGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pchypregettype_ pchypregettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcmggalerkinsetmatproductalgorithm_ PCMGGALERKINSETMATPRODUCTALGORITHM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmggalerkinsetmatproductalgorithm_ pcmggalerkinsetmatproductalgorithm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcmggalerkingetmatproductalgorithm_ PCMGGALERKINGETMATPRODUCTALGORITHM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcmggalerkingetmatproductalgorithm_ pcmggalerkingetmatproductalgorithm
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  pchypresetdiscretegradient_(PC pc,Mat G, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(G);
*ierr = PCHYPRESetDiscreteGradient(
	(PC)PetscToPointer((pc) ),
	(Mat)PetscToPointer((G) ));
}
PETSC_EXTERN void  pchypresetdiscretecurl_(PC pc,Mat C, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(C);
*ierr = PCHYPRESetDiscreteCurl(
	(PC)PetscToPointer((pc) ),
	(Mat)PetscToPointer((C) ));
}
PETSC_EXTERN void  pchypresetinterpolations_(PC pc,PetscInt *dim,Mat RT_PiFull,Mat RT_Pi[],Mat ND_PiFull,Mat ND_Pi[], int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(RT_PiFull);
PetscBool RT_Pi_null = !*(void**) RT_Pi ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(RT_Pi);
CHKFORTRANNULLOBJECT(ND_PiFull);
PetscBool ND_Pi_null = !*(void**) ND_Pi ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(ND_Pi);
*ierr = PCHYPRESetInterpolations(
	(PC)PetscToPointer((pc) ),*dim,
	(Mat)PetscToPointer((RT_PiFull) ),RT_Pi,
	(Mat)PetscToPointer((ND_PiFull) ),ND_Pi);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! RT_Pi_null && !*(void**) RT_Pi) * (void **) RT_Pi = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! ND_Pi_null && !*(void**) ND_Pi) * (void **) ND_Pi = (void *)-2;
}
PETSC_EXTERN void  pchypresetalphapoissonmatrix_(PC pc,Mat A, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(A);
*ierr = PCHYPRESetAlphaPoissonMatrix(
	(PC)PetscToPointer((pc) ),
	(Mat)PetscToPointer((A) ));
}
PETSC_EXTERN void  pchypresetbetapoissonmatrix_(PC pc,Mat A, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(A);
*ierr = PCHYPRESetBetaPoissonMatrix(
	(PC)PetscToPointer((pc) ),
	(Mat)PetscToPointer((A) ));
}
PETSC_EXTERN void  pchypresetedgeconstantvectors_(PC pc,Vec ozz,Vec zoz,Vec zzo, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(ozz);
CHKFORTRANNULLOBJECT(zoz);
CHKFORTRANNULLOBJECT(zzo);
*ierr = PCHYPRESetEdgeConstantVectors(
	(PC)PetscToPointer((pc) ),
	(Vec)PetscToPointer((ozz) ),
	(Vec)PetscToPointer((zoz) ),
	(Vec)PetscToPointer((zzo) ));
}
PETSC_EXTERN void  pchypreamssetinteriornodes_(PC pc,Vec interior, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(interior);
*ierr = PCHYPREAMSSetInteriorNodes(
	(PC)PetscToPointer((pc) ),
	(Vec)PetscToPointer((interior) ));
}
PETSC_EXTERN void  pchypresettype_(PC pc, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(pc);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PCHYPRESetType(
	(PC)PetscToPointer((pc) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  pchypregettype_(PC pc, char *name, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(pc);
*ierr = PCHYPREGetType(
	(PC)PetscToPointer((pc) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for name */
*ierr = PetscStrncpy(name, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, name, cl0);
}
PETSC_EXTERN void  pcmggalerkinsetmatproductalgorithm_(PC pc, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(pc);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PCMGGalerkinSetMatProductAlgorithm(
	(PC)PetscToPointer((pc) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  pcmggalerkingetmatproductalgorithm_(PC pc, char *name, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(pc);
*ierr = PCMGGalerkinGetMatProductAlgorithm(
	(PC)PetscToPointer((pc) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for name */
*ierr = PetscStrncpy(name, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, name, cl0);
}
#if defined(__cplusplus)
}
#endif
