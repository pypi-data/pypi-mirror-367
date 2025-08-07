#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* gamg.c */
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
#include "petscksp.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgamgsetproceqlim_ PCGAMGSETPROCEQLIM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgamgsetproceqlim_ pcgamgsetproceqlim
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgamgsetcoarseeqlim_ PCGAMGSETCOARSEEQLIM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgamgsetcoarseeqlim_ pcgamgsetcoarseeqlim
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgamgsetrepartition_ PCGAMGSETREPARTITION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgamgsetrepartition_ pcgamgsetrepartition
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgamgsetusesaesteig_ PCGAMGSETUSESAESTEIG
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgamgsetusesaesteig_ pcgamgsetusesaesteig
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgamgsetrecomputeesteig_ PCGAMGSETRECOMPUTEESTEIG
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgamgsetrecomputeesteig_ pcgamgsetrecomputeesteig
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgamgseteigenvalues_ PCGAMGSETEIGENVALUES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgamgseteigenvalues_ pcgamgseteigenvalues
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgamgsetreuseinterpolation_ PCGAMGSETREUSEINTERPOLATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgamgsetreuseinterpolation_ pcgamgsetreuseinterpolation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgamgasmsetuseaggs_ PCGAMGASMSETUSEAGGS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgamgasmsetuseaggs_ pcgamgasmsetuseaggs
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgamgsetparallelcoarsegridsolve_ PCGAMGSETPARALLELCOARSEGRIDSOLVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgamgsetparallelcoarsegridsolve_ pcgamgsetparallelcoarsegridsolve
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgamgsetcpupincoarsegrids_ PCGAMGSETCPUPINCOARSEGRIDS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgamgsetcpupincoarsegrids_ pcgamgsetcpupincoarsegrids
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgamgsetcoarsegridlayouttype_ PCGAMGSETCOARSEGRIDLAYOUTTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgamgsetcoarsegridlayouttype_ pcgamgsetcoarsegridlayouttype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgamgsetnlevels_ PCGAMGSETNLEVELS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgamgsetnlevels_ pcgamgsetnlevels
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgamgasmsethem_ PCGAMGASMSETHEM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgamgasmsethem_ pcgamgasmsethem
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgamgsetthreshold_ PCGAMGSETTHRESHOLD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgamgsetthreshold_ pcgamgsetthreshold
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgamgsetrankreductionfactors_ PCGAMGSETRANKREDUCTIONFACTORS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgamgsetrankreductionfactors_ pcgamgsetrankreductionfactors
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgamgsetthresholdscale_ PCGAMGSETTHRESHOLDSCALE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgamgsetthresholdscale_ pcgamgsetthresholdscale
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgamgsettype_ PCGAMGSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgamgsettype_ pcgamgsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgamggettype_ PCGAMGGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgamggettype_ pcgamggettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgamgsetinjectionindex_ PCGAMGSETINJECTIONINDEX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgamgsetinjectionindex_ pcgamgsetinjectionindex
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgamgcreategraph_ PCGAMGCREATEGRAPH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgamgcreategraph_ pcgamgcreategraph
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  pcgamgsetproceqlim_(PC pc,PetscInt *n, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCGAMGSetProcEqLim(
	(PC)PetscToPointer((pc) ),*n);
}
PETSC_EXTERN void  pcgamgsetcoarseeqlim_(PC pc,PetscInt *n, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCGAMGSetCoarseEqLim(
	(PC)PetscToPointer((pc) ),*n);
}
PETSC_EXTERN void  pcgamgsetrepartition_(PC pc,PetscBool *n, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCGAMGSetRepartition(
	(PC)PetscToPointer((pc) ),*n);
}
PETSC_EXTERN void  pcgamgsetusesaesteig_(PC pc,PetscBool *b, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCGAMGSetUseSAEstEig(
	(PC)PetscToPointer((pc) ),*b);
}
PETSC_EXTERN void  pcgamgsetrecomputeesteig_(PC pc,PetscBool *b, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCGAMGSetRecomputeEstEig(
	(PC)PetscToPointer((pc) ),*b);
}
PETSC_EXTERN void  pcgamgseteigenvalues_(PC pc,PetscReal *emax,PetscReal *emin, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCGAMGSetEigenvalues(
	(PC)PetscToPointer((pc) ),*emax,*emin);
}
PETSC_EXTERN void  pcgamgsetreuseinterpolation_(PC pc,PetscBool *n, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCGAMGSetReuseInterpolation(
	(PC)PetscToPointer((pc) ),*n);
}
PETSC_EXTERN void  pcgamgasmsetuseaggs_(PC pc,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCGAMGASMSetUseAggs(
	(PC)PetscToPointer((pc) ),*flg);
}
PETSC_EXTERN void  pcgamgsetparallelcoarsegridsolve_(PC pc,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCGAMGSetParallelCoarseGridSolve(
	(PC)PetscToPointer((pc) ),*flg);
}
PETSC_EXTERN void  pcgamgsetcpupincoarsegrids_(PC pc,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCGAMGSetCpuPinCoarseGrids(
	(PC)PetscToPointer((pc) ),*flg);
}
PETSC_EXTERN void  pcgamgsetcoarsegridlayouttype_(PC pc,PCGAMGLayoutType *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCGAMGSetCoarseGridLayoutType(
	(PC)PetscToPointer((pc) ),*flg);
}
PETSC_EXTERN void  pcgamgsetnlevels_(PC pc,PetscInt *n, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCGAMGSetNlevels(
	(PC)PetscToPointer((pc) ),*n);
}
PETSC_EXTERN void  pcgamgasmsethem_(PC pc,PetscInt *n, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCGAMGASMSetHEM(
	(PC)PetscToPointer((pc) ),*n);
}
PETSC_EXTERN void  pcgamgsetthreshold_(PC pc,PetscReal v[],PetscInt *n, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLREAL(v);
*ierr = PCGAMGSetThreshold(
	(PC)PetscToPointer((pc) ),v,*n);
}
PETSC_EXTERN void  pcgamgsetrankreductionfactors_(PC pc,PetscInt v[],PetscInt *n, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLINTEGER(v);
*ierr = PCGAMGSetRankReductionFactors(
	(PC)PetscToPointer((pc) ),v,*n);
}
PETSC_EXTERN void  pcgamgsetthresholdscale_(PC pc,PetscReal *v, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCGAMGSetThresholdScale(
	(PC)PetscToPointer((pc) ),*v);
}
PETSC_EXTERN void  pcgamgsettype_(PC pc,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(pc);
/* insert Fortran-to-C conversion for type */
  FIXCHAR(type,cl0,_cltmp0);
*ierr = PCGAMGSetType(
	(PC)PetscToPointer((pc) ),_cltmp0);
  FREECHAR(type,_cltmp0);
}
PETSC_EXTERN void  pcgamggettype_(PC pc,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(pc);
*ierr = PCGAMGGetType(
	(PC)PetscToPointer((pc) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for type */
*ierr = PetscStrncpy(type, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, type, cl0);
}
PETSC_EXTERN void  pcgamgsetinjectionindex_(PC pc,PetscInt *n,PetscInt idx[], int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLINTEGER(idx);
*ierr = PCGAMGSetInjectionIndex(
	(PC)PetscToPointer((pc) ),*n,idx);
}
PETSC_EXTERN void  pcgamgcreategraph_(PC pc,Mat A,Mat *G, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(A);
PetscBool G_null = !*(void**) G ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(G);
*ierr = PCGAMGCreateGraph(
	(PC)PetscToPointer((pc) ),
	(Mat)PetscToPointer((A) ),G);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! G_null && !*(void**) G) * (void **) G = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
